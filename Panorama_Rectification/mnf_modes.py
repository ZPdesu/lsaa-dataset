# mnf_modes.py
import ctypes
import os

# Try to locate the .so file in the same directory as this file
_file = 'libmnf_modes.so'
_path = os.path.join(*(os.path.split(__file__)[:-1] + (_file,)))
_mod = ctypes.cdll.LoadLibrary(_path)



print(_mod)



# void avg(double *, int n)
# Define a special type for the 'double *' argument
class DoubleArrayType:
    def from_param(self, param):
        typename = type(param).__name__
        if hasattr(self, 'from_' + typename):
            return getattr(self, 'from_' + typename)(param)
        elif isinstance(param, ctypes.Array):
            return param
        else:
            raise TypeError("Can't convert %s" % typename)

    # Cast from array.array objects
    def from_array(self, param):
        if param.typecode != 'd':
            raise TypeError('must be an array of doubles')
        ptr, _ = param.buffer_info()
        return ctypes.cast(ptr, ctypes.POINTER(ctypes.c_double))

    # Cast from lists/tuples
    def from_list(self, param):
        val = ((ctypes.c_double)*len(param))(*param)
        return val

    from_tuple = from_list

    # Cast from a numpy array
    def from_ndarray(self, param):
        return param.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

DoubleArray1 = DoubleArrayType()
DoubleArray2 = DoubleArrayType()
DoubleArray3 = DoubleArrayType()
_mnf = _mod.mnf
_mnf.argtypes = (DoubleArray1, ctypes.c_int, ctypes.c_double, DoubleArray2, DoubleArray3)
_mnf.restype = ctypes.c_int

def mnf(histo, N, epsilon, outArray1, outArray2):
    return _mnf(histo, N, epsilon, outArray1, outArray2)



