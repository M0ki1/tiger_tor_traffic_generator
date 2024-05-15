import numpy as np
import ZipfGenerator

#x = random.zipf(a=2, size=(2, 3))

a=2
s = np.random.zipf(a, 50)
result = (s/float(max(s)))*1000

print("s", s)
print(min(s), max(s))
print(min(result), max(result))
"""

"""
from numpy import random
import matplotlib.pyplot as plt
import seaborn as sns


np.set_printoptions(suppress=True)



N_ONIONS = 32
#N_ONIONS = 16
#N_REQUESTS = 10000
N_REQUESTS = 100000

ALPHA = 1.5

print("Probabilities: ", probabilities)
occurrences = {}
numbers = []
print_str = '['
for i in range(0, N_ONIONS):
    occurrences[i] = 0

generator = ZipfGenerator.LoadGenerator(N_ONIONS, ALPHA)
for i in range(0, N_REQUESTS):
    number = generator.next()
    occurrences[number] += 1
    numbers.append(number)

probabilities = np.array(list(occurrences.values()))
print(probabilities)
probabilities = probabilities / N_REQUESTS
# sort array in descending order
probabilities[::-1].sort()

for prob in probabilities:
    print_str += '"{0:04.0f}",'.format(prob * 10000)
print_str += ']'

print("String to intro: ", print_str)
print("Probabilities: ", probabilities)
##################
print("new format: \n[")
len_p = len(probabilities)
new_format = [[] for i in range(int(len_p/4))]
aux_format = []
j = 0
for i in range(0, len_p, 4):
    aux_format += [int(i/4)]
    aux_format += [len_p-(j+1), len_p-(j+2), len_p-(j+3)]
    j += 3
for i in range(int(len_p/4)):
    new_format[i] += [probabilities[p] for p in aux_format[i*4:i*4+4]]
for f in new_format:
    print("[{0}]".format(', '.join(map(str, ["\"" + str(p) + "\"" for p in f]))), end=",\n")
print("]")
##################
print("Sum: ", sum(probabilities))

sns.distplot(numbers, kde=False)
plt.show()