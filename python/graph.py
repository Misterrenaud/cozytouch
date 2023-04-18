#!/usr/bin/python3
__author__ = "Renaud Loiseleux"
__email__ = "renaud.loiseleux@gmail.com"
import matplotlib.pyplot as plt
import pandas as pd

from cozytouch.history import History

snapshots = History().get_today_s_snapshots()

dates = [s.ts for s in snapshots]
#data["date"] = pd.to_datetime(data["date"])

values = [s.get_temps() for s in snapshots]
ids = list(values[0].keys())
print(ids)

for id in ids:
    plt.plot(dates, [v[id] for v in values], label=id)
plt.legend()

plt.show()