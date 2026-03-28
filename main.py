#!/usr/bin/env python

import os.path, string, sys

# Add the parent directory to the system path so packaging can be imported
sys.path.append("..")

# Import the packaging module and its utilities
import packaging
from packaging import progress, utils

# Import PIL for image creation and drawing
from PIL import Image, ImageDraw


class _Color:
    """
    Base class for all color schemes used in MalVis.
    Stores the raw byte data and an optional highlight block.
    All visualization methods inherit from this class.
    """

    def __init__(self, data, block):
        # Store the raw byte data and the optional highlight block
        self.data, self.block = data, block

        # Build a sorted list of unique byte values and map each to an index
        s = list(set(data))
        s.sort()
        self.symbol_map = {v: i for (i, v) in enumerate(s)}

    def __len__(self):
        # Return the total number of bytes in the data
        return len(self.data)

    def point(self, x):
        # If the current position falls inside the highlight block, return the block color
        # Otherwise, delegate to the subclass color computation
        if self.block and (self.block[0] <= x < self.block[1]):
            return self.block[2]
        else:
            return self.getPoint(x)


class Entropy(_Color):
    """
    Entropy visualization method.
    Maps each byte position to an RGB color based on the local Shannon entropy
    computed over a sliding window of 32 bytes.

    Red channel: a nonlinear curve applied to entropy values above 0.5,
                 highlighting regions of high randomness such as encrypted or compressed data.
    Green channel: always zero in this method.
    Blue channel: the square of the entropy value, growing smoothly from low to high entropy.

    This method is based on the original work by Cortesi.
    """

    def getPoint(self, x):
        # Compute the local entropy over a 32 byte window centered at position x
        e = utils.entropy(self.data, 32, x, len(self.symbol_map))

        # Nonlinear curve function that amplifies mid to high entropy values
        # The formula produces a peak around entropy value 0.75
        def curve(v):
            f = (4 * v - 4 * v**2) ** 4
            f = max(f, 0)
            return f

        # Red is driven by the curve and only activates when entropy exceeds 0.5
        r = curve(e - 0.5) if e > 0.5 else 0

        # Blue grows as a square of the entropy, giving a smooth gradient
        b = e**2

        return [int(255 * r), 0, int(255 * b)]


class MalVis_Classbyte(_Color):
    """
    MalVis Classbyte visualization method.
    Extends the Entropy method by encoding byte class information into the green channel.

    Each byte is classified into one of four categories:
        Null byte (value 0)       mapped to black   (green = 0)
        Padding byte (value 255)  mapped to white   (green = 255)
        Printable ASCII byte      mapped to blue    (green = 85)
        Non-printable byte        mapped to red     (green = 170)

    The red and blue channels remain identical to the Entropy method, as shown in our first paper.
    This produces full RGB images that reveal structural patterns in the bytecode.
    """

    def getPoint(self, x):
        # Read the byte value at position x, handling both int and char types
        if isinstance(self.data[x], int):
            c = self.data[x]
        else:
            c = ord(self.data[x])

        # Assign a green channel value based on the byte class
        if c == 0:
            g = 0          # Null byte displayed as black
        elif c == 255:
            g = 255        # Padding byte displayed as white
        elif chr(c) in string.printable:
            g = 85         # Printable ASCII byte displayed as blue
        else:
            g = 170        # Non printable byte displayed as red

        # Compute local entropy over a 32 byte window
        e = utils.entropy(self.data, 32, x, len(self.symbol_map))

        # Same nonlinear curve used in the Entropy method
        def curve(v):
            f = (4 * v - 4 * v**2) ** 4
            f = max(f, 0)
            return f

        # Red and blue channels are computed the same way as in Entropy
        r = curve(e - 0.5) if e > 0.5 else 0
        b = e**2

        return [int(255 * r), int(g), int(255 * b)]


class MalVis_Ngram(_Color):
    """
    MalVis-N-gram visualization method.
    Extends the Entropy method by encoding bigram (2-byte window) information
    into the green channel.

    For each position x, the bigram value is formed by combining byte x and byte x+1.
    This value is normalized to the range 0 to 1 and mapped to the green channel.
    At the last byte position where no full bigram can be formed, green is set to zero.

    The red and blue channels remain identical to the Entropy method.
    This method captures sequential byte transition patterns within the bytecode.
    """

    def getPoint(self, x):
        # Compute local entropy over a 32 byte window
        e = utils.entropy(self.data, 32, x, len(self.symbol_map))

        # Same nonlinear curve used in the Entropy method
        def curve(v):
            f = (4 * v - 4 * v**2) ** 4
            f = max(f, 0)
            return f

        # Red and blue channels are computed the same way as in Entropy
        r = curve(e - 0.5) if e > 0.5 else 0
        b = e**2

        # Form a bigram from the current byte and the next byte
        # The 16-bit value is normalized to fit in the range 0 to 1
        if x < len(self.data) - 1:
            ngram_value = (self.data[x] << 8) + self.data[x + 1]
            g = ngram_value / 65535.0
        else:
            # Last byte cannot form a complete bigram, so green defaults to zero
            g = 0

        return [int(255 * r), int(255 * g), int(255 * b)]


def drawmap_square(map, size, csource, name, prog):
    """
    Renders the visualization as a square PNG image using a Hilbert curve layout.
    Each pixel corresponds to a byte in the input file, colored by the chosen method.
    The image is saved to the path specified by name.
    """

    # Set the total number of pixels to render
    prog.set_target((size**2))

    # Map the data layout to a Hilbert curve of the given size
    map = packaging.fromSize(map, 2, size**2)

    # Create a blank RGB image and prepare a drawing context
    c = Image.new("RGB", map.dimensions())
    cd = ImageDraw.Draw(c)

    # Compute the step size to sample the color source evenly across all pixels
    step = len(csource) / float(len(map))

    # Draw each pixel with the color returned by the active color scheme
    for i, p in enumerate(map):
        color = csource.point(int(i * step))
        cd.point(tuple(p), fill=tuple(color))

        # Update the progress bar every 100 pixels
        if not i % 100:
            prog.tick(i)

    # Save the completed image to disk
    c.save(name)


def main():
    from optparse import OptionParser, OptionGroup

    parser = OptionParser(
        usage="%prog [options] infile [output]",
        description=(
            "Welcome to the MalVis tool. "
            "This tool converts a .dex file into a .png visualization. "
            "Use the options below to select a color scheme, image size, and output behavior. "
            'For a full list of options, type "%prog --help".'
        ),
        version="%prog 0.1"
    )

    parser.add_option(
        "-c",
        "--color",
        action="store",
        type="choice",
        dest="color",
        default="entropy",
        choices=["entropy", "malvis_classbyte", "malvis_ngram"],
        help=(
            "Select a color scheme. "
            "Use 'entropy' for the original entropy representation. "
            "Use 'malvis_classbyte' for entropy combined with byte class encoding. "
            "Use 'malvis_ngram' for entropy combined with bigram encoding. "
            "The default is 'entropy'."
        ),
    )

    parser.add_option(
        "-q",
        "--quite",
        action="store_true",
        default=False,
        dest="progress",
        help="Suppress the progress bar and print only the output file name.",
    )

    parser.add_option(
        "-s",
        "--size",
        action="store",
        type="int",
        dest="size",
        default=256,
        help="Output image width in pixels. The default is 256.",
    )

    options, args = parser.parse_args()

    # Require at least one argument (input file) and at most two (input and output)
    if len(args) not in [1, 2]:
        parser.error("Please specify an input file and an optional output file.")

    # Read the input .dex file as raw bytes
    with open(args[0], "rb") as file:
        d = file.read()

    # Determine the output file path
    if len(args) == 2:
        dst = args[1]
    else:
        base = os.path.basename(args[0])
        if "." in base:
            base, _ = base.rsplit(".", 1)
        dst = base + options.suffix + ".png"

    # Prevent accidental overwriting of an existing file unless explicitly specified
    if os.path.exists(dst) and len(args) < 2:
        print >> sys.stderr, "Refusing to overwrite '%s'. Specify the output path explicitly to overwrite." % dst
        sys.exit(1)

    block = None

    # Instantiate the selected color scheme
    if options.color == "entropy":
        csource = Entropy(d, block)
    elif options.color == "malvis_classbyte":
        csource = MalVis_Classbyte(d, block)
    elif options.color == "malvis_ngram":
        csource = MalVis_Ngram(d, block)
    else:
        csource = Entropy(d, block)

    # Set up the progress tracker based on user preference
    if options.progress:
        print(dst)
        prog = progress.Dummy()
    else:
        prog = progress.Progress(None)

    # Generate and save the visualization
    drawmap_square("hilbert", options.size, csource, dst, prog)
    prog.clear()


main()
