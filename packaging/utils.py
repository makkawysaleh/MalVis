import math

def graycode(x):
    # Convert an integer to its Gray code representation
    x = int(x)  # Cast x to an integer
    return x ^ (x >> 1)


"""
    Inverse gray code.
"""
def igraycode(x):

    if x == 0:
        return x
    m = int(math.ceil(math.log(x, 2)))+1
    i, j = x, 1
    while j < m:
        i = i ^ (x>>j)
        j += 1
    return i

"""
    Convert n to a list of bits of length width.
"""
def bits(n, width):
   
    assert n < 2**width
    bin = []
    for i in range(width):
        bin.insert(0, 1 if n&(1<<i) else 0)
    return bin


"""
    Convert a list of bits to an integer.
"""
def bits2int(bits):    
    n = 0
    for p, i in enumerate(reversed(bits)):
        n += i*2**p
    return n

"""
    Right bit-rotation.

    width: the bit width of x.
"""
def rrot(x, i, width):

    assert x < 2**width
    i = i%width
    x = (x>>i) | (x<<width-i)
    return x&(2**width-1)

"""
    Left bit-rotation.

    width: the bit width of x.
"""
def lrot(x, i, width):
    assert x < 2**width
    i = i%width
    x = (x<<i) | (x>>width-i)
    return x&(2**width-1)

"""
    Trailing set bits.
"""
def tsb(x, width):
    assert x < 2**width
    i = 0
    while x&1 and i <= width:
        x = x >> 1
        i += 1
    return i

"""
    Sets bit i in an integer x of width w to b.
    b must be 1 or 0
"""
def setbit(x, w, i, b):
    assert b in [1, 0]
    assert i < w
    if b:
        return x | 2**(w-i-1)
    else:
        return x & ~2**(w-i-1)

"""
    Extract a bit range as an integer.
    (start, end) is inclusive lower bound, exclusive upper bound.
"""
def bitrange(x, width, start, end):
    return x >> (width-end) & ((2**(end-start))-1)

"""
    Returns local  entropy for a location in a file.
"""
def entropy(data, blocksize, offset, symbols=256):
    if len(data) < blocksize:
        raise ValueError("Data length must be larger than block size.")
    if offset < blocksize/2:
        start = 0
    elif offset > len(data)-blocksize/2:
        start = len(data)-blocksize/2
    else:
        start = offset-blocksize/2
    hist = {}
    for i in data[int(start):int(start+blocksize)]:
        hist[i] = hist.get(i, 0) + 1
    base = min(blocksize, symbols)
    entropy = 0
    for i in hist.values():
        p = i/float(blocksize)
        # If blocksize < 256, the number of possible byte values is restricted.
        # In that case, we adjust the log base to make sure we get a value
        # between 0 and 1.
        entropy += (p * math.log(p, base))
    return -entropy
