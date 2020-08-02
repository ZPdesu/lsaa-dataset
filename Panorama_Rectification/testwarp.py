import numpy as np
import skimage.transform
import skimage.io



a = skimage.io.imread('0801.jpg')
height = a.shape[0]
width = a.shape[1]

trans = np.array([[1,0,800], [0, 1, 0], [0, 0, 1]])
trans2 = np.array([[1,0,-800], [0, 1, 0], [0, 0, 1]])
b = skimage.transform.warp(a, trans2.dot(trans), output_shape = [1200, 1600])


skimage.io.imsave('test_output.jpg', b)

