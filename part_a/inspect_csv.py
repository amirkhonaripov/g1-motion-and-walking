import sys
import numpy as np

csv_path = sys.argv[1]

csv_read = np.loadtxt(csv_path, delimiter=",")
print("(rows, columns):", csv_read.shape)
print("row 0:", csv_read[0])

stdev = np.std(csv_read, axis=0)
stdev_sorted = np.argsort(stdev)[::-1]
print("col_indices_sorted:", stdev_sorted[:10])
print("std_values_sorted:", stdev[stdev_sorted[:10]])

