import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import csv
import numpy as np

with open('results.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    resultX = reader.__next__()
    resultY = reader.__next__()

x = list(np.float_(resultX))
y = list(np.float_(resultY))

plt.scatter(x, y)
plt.show()