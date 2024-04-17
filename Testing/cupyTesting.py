import cupy as np
import numpy as slow
import time

randomValues = np.random.random_sample((1000,1000))
start = time.time()
mean = np.mean(randomValues)
end = time.time()
print(start - end)