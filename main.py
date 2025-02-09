#!/usr/bin/env python
import os.path, string, sys

# calling the packaging directory
sys.path.append("..")
# ---- importing packaging
import packaging
from packaging import progress, utils
# ---- importing PIL for drawing
from PIL import Image, ImageDraw


class _Color:
    def __init__(self, data, block):
        self.data, self.block = data, block
        s = list(set(data))
        s.sort()
        self.symbol_map = {v: i for (i, v) in enumerate(s)}

    def __len__(self):
        return len(self.data)

    def point(self, x):
        if self.block and (self.block[0] <= x < self.block[1]):
            return self.block[2]
        else:
            return self.getPoint(x)




class Entropy(_Color):
    def getPoint(self, x):
        e = utils.entropy(self.data, 32, x, len(self.symbol_map))

        def curve(v):
            f = (4 * v - 4 * v**2) ** 4
            f = max(f, 0)
            return f

        r = curve(e - 0.5) if e > 0.5 else 0
        b = e**2
        return [int(255 * r), 0, int(255 * b)]


# --------------------- NEW ------------------
class MalVis_A(_Color):
    def getPoint(self, x):
        if isinstance(self.data[x], int):
            c = self.data[x]
        else:
            c = ord(self.data[x])

        if c == 0:
            g = 0  # Black
        elif c == 255:
            g = 255  # White
        elif chr(c) in string.printable:  # Blue
            g = 85  # Blue printable
        else:
            g = 170  # Red not printable
        e = utils.entropy(self.data, 32, x, len(self.symbol_map))

        def curve(v):
            f = (4 * v - 4 * v**2) ** 4
            f = max(f, 0)
            return f

        r = curve(e - 0.5) if e > 0.5 else 0
        b = e**2
        return [int(255 * r), int(g), int(255 * b)]

# ------------------- New code for N-gram of 2 bytes --------------------------------
class MalVis_B(_Color):
    def getPoint(self, x):
        e = utils.entropy(self.data, 32, x, len(self.symbol_map))

        def curve(v):
            f = (4 * v - 4 * v**2) ** 4
            f = max(f, 0)
            return f

        r = curve(e - 0.5) if e > 0.5 else 0
        b = e**2

        # Compute n-gram (window of two bytes)
        if x < len(self.data) - 1:
            ngram_value = (self.data[x] << 8) + self.data[x + 1]
            g = ngram_value / 65535.0  # Normalizing to fit in the range [0, 1]
        else:
            g = 0  # If we're at the last byte, we can't form a full n-gram

        return [int(255 * r), int(255 * g), int(255 * b)]
    

def drawmap_square(map, size, csource, name, prog):
    prog.set_target((size**2))
    map = packaging.fromSize(map, 2, size**2)
    c = Image.new("RGB", map.dimensions())
    cd = ImageDraw.Draw(c)
    step = len(csource) / float(len(map))
    for i, p in enumerate(map):
        color = csource.point(int(i * step))
        cd.point(tuple(p), fill=tuple(color))
        if not i % 100:
            prog.tick(i)
    c.save(name)


def main():
    from optparse import OptionParser, OptionGroup

    parser = OptionParser(
        usage="%prog [options] infile [output]",
        description="""Welcome to MalVis tool! Use the options below to customize your visualization.\n
        \n
        This tool takes .dex file as input and generates a .png file as output.
        For information about the options, type "%prog --help".""",
        version="%prog 0.1"
    )

    parser.add_option(
        "-c",
        "--color",
        action="store",
        type="choice",
        dest="color",
        default="entropy",
        choices=[ "entropy", "malvis_a","malvis_b"],
        help="Select a color scheme. Choose from the following MalVis representation options: 'entropy' for the original entropy representation, 'malvis_a' for a new approach using entropy with classbyte representation, or 'malvis_b' for a new approach using entropy with n-gram representation. The default selection is 'entropy'.",
        )

    parser.add_option(
        "-q",
        "--quite",
        action="store_true",
        default=False,
        dest="progress",
        help="Don't show progress bar - print the destination file name.",
    )
    parser.add_option(
        "-s",
        "--size",
        action="store",
        type="int",
        dest="size",
        default=256,
        help="Image width in pixels.",
    )

    
    options, args = parser.parse_args()
    if len(args) not in [1, 2]:
        parser.error("Please specify input and output file.")
    
    # Load data from the file.dex as bytes
    with open(args[0], "rb") as file:
        d = file.read()

    if len(args) == 2:
        dst = args[1]
    else:
        base = os.path.basename(args[0])
        if "." in base:
            base, _ = base.rsplit(".", 1)
        dst = base + options.suffix + ".png"

    if os.path.exists(dst) and len(args) < 2:
        print >> sys.stderr, "Refusing to over-write '%s'. Specify explicitly if you really want to do this." % dst
        sys.exit(1)

    block = None


    if options.color == "entropy":
        csource = Entropy(d, block)

    elif options.color == "malvis_a":
        csource = MalVis_A(d, block)

    elif options.color == 'malvis_b':
        csource = MalVis_B(d, block)

    else:
        csource = Entropy(d, block)

    if  options.progress:
        print(dst)
        prog = progress.Dummy()
    else:
        prog = progress.Progress(None)
    
    drawmap_square("hilbert", options.size, csource, dst, prog)
    prog.clear()


main()
