
from . import hilbert

curveMap = {
    "hilbert": hilbert.Hilbert,
}
curves = curveMap.keys()

"""
        Function for creating a curve by taking a specified
        size and dimension. 
"""
def fromSize(curve, dimension, size):
    return curveMap[curve].fromSize(dimension, size)

"""
    Function for creating a curve by taking
    order and dimension.
"""
def fromOrder(curve, dimension, order):
    return curveMap[curve](dimension, order)
