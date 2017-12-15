import numpy as np

arr = np.zeros((1,3), dtype = int)
arr2 = np.append(arr, arr, axis=0)
arr2 = np.append(arr2, arr, axis = 0)
arr2 = np.append(arr2, arr, axis = 0)

print(arr2.shape)
print(arr2)
