from . import utils
import math


def transform(entry, direction, width, x):
    # Apply a transformation to the entry based on direction and width
    assert x < 2**width
    assert entry < 2**width
    return utils.rrot((x^entry), direction+1, width)

"""
Inverse transform - we simply reverse the operations in transform.
"""
def itransform(entry, direction, width, x):
    assert x < 2**width
    assert entry < 2**width
    return utils.lrot(x, direction+1, width)^entry
    # There is an error in the Hamilton paper's formulation of the inverse
    # transform in Lemma 2.12. The correct restatement as a transform is as follows:
    # return transform(rrot(entry, direction+1, width), width-direction-2, width, x)


def direction(x, n):
    # Determine the direction based on the value of x and n
    assert x < 2**n
    if x == 0:
        return 0
    elif x % 2 == 0:
        return utils.tsb(x-1, n) % n
    else:
        return utils.tsb(x, n) % n


def entry(x):
    # Calculate the entry value based on x
    if x == 0:
        return 0
    else:
        return utils.graycode(2 * ((x-1) / 2))

"""
Convert an index on the Hilbert curve of the specified dimension and
order to a set of point coordinates.
"""
def hilbert_point(dimension, order, h):
    hwidth = order * dimension
    e, d = 0, 0
    p = [0] * dimension
    for i in range(order):
        w = utils.bitrange(h, hwidth, i * dimension, i * dimension + dimension)
        l = utils.graycode(w)
        l = itransform(e, d, dimension, l)
        for j in range(dimension):
            b = utils.bitrange(l, dimension, j, j + 1)
            p[j] = utils.setbit(p[j], order, i, b)
        e = e ^ utils.lrot(entry(w), d + 1, dimension)
        d = (d + direction(w, dimension) + 1) % dimension
    return p


def hilbert_index(dimension, order, p):
    # Convert a set of point coordinates to an index on the Hilbert curve
    h, e, d = 0, 0, 0
    for i in range(order):
        l = 0
        for x in range(dimension):
            b = utils.bitrange(p[dimension - x - 1], order, i, i + 1)
            l |= b << x
        l = transform(e, d, dimension, l)
        w = utils.igraycode(l)
        e = e ^ utils.lrot(entry(w), d + 1, dimension)
        d = (d + direction(w, dimension) + 1) % dimension
        h = (h << dimension) | w
    return h


class Hilbert:
    def __init__(self, dimension, order):
        # Initialize the Hilbert class with dimension and order
        self.dimension, self.order = dimension, order

    @classmethod
    def fromSize(cls, dimension, size):
        """
        Create a Hilbert curve from the given size.
        Size is the total number of points in the curve.
        """
        x = math.log(size, 2)
        if not float(x) / dimension == int(x) / dimension:
            raise ValueError("Size does not fit Hilbert curve of dimension %s." % dimension)
        return Hilbert(dimension, int(x / dimension))

    def __len__(self):
        # Return the total number of points in the Hilbert curve
        return 2**(self.dimension * self.order)

    def __getitem__(self, idx):
        # Get the point at the given index
        if idx >= len(self):
            raise IndexError
        return self.point(idx)
    """
    Return the size of this curve in each dimension.
    """
    def dimensions(self):
        return [int(math.ceil(len(self) ** (1 / float(self.dimension))))] * self.dimension

    def index(self, p):
        # Get the index of the given point
        return hilbert_index(self.dimension, self.order, p)

    def point(self, idx):
        # Get the point at the given index
        return hilbert_point(self.dimension, self.order, idx)

