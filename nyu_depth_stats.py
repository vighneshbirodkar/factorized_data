import numpy as np
import csv
from matplotlib import pyplot as plt


counts = {}
with open('../SUNCGtoolbox/metadata/ModelCategoryMapping.csv') as f:
    reader = csv.reader(f)
    first = True
    for row in reader:
        if first:
            first = False
            continue
        nyud_class = row[5]
        counts[nyud_class] = counts.get(nyud_class, 0) + 1

classes = sorted(counts.keys(), key=lambda k: counts[k], reverse=True)
print(sorted(classes))
counts = [counts[c] for c in classes]

fig, ax = plt.subplots()

width = 0.5
ind = np.arange(len(classes))
ax.bar(ind, counts, width=width)
ax.set_xticks(ind + 0*width / 2)


ax.set_xticklabels(classes, rotation='vertical')
ax.set_xlabel('Classes')
ax.set_ylabel('Number of Samples')

plt.show()
