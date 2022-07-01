
ALICETRD2018/tracksum.py /
@WianZeeman
WianZeeman Save data before plotting
History
1 contributor
82 lines (75 sloc) 2.51 KB
"""python3 tracksum.py file
Plot a histograms of tracklet events from a data file.
Paramters
---------
file : relative path to a data file
"""
import sys
import o32reader as rdr
import adcarray as adc
import numpy as np
import defaults
import matplotlib as mpl
import matplotlib.pyplot as plt

if len(sys.argv) != 2:
    print('Incorrect use of tracksum.py.  Type', file=sys.stderr)
    print('python3 tracksum.py file', file=sys.stderr)
    print('where file is the path to a data file.', file=sys.stderr)
    sys.exit()
reader = rdr.o32reader(sys.argv[1])
analyser = adc.adcarray()
bins = np.linspace(1, 14000, 2000)
main, bin_edges = np.histogram([], bins)
edges, bin_edges = np.histogram([], bins)
for evno, raw_data in enumerate(reader):
    if evno % defaults.PRINT_EVNO_EVERY == 0:
        print("Proccessing events %d–%d"
                % (evno, evno + defaults.PRINT_EVNO_EVERY))

    if evno == 0:
        # Skip the first event as it may be a configuration event
        # depending on run configurations.
        continue 

    try:
        analyser.analyse_event(raw_data)
    except adc.datafmt_error as e:
        continue
    data = analyser.data[:12] # The last four rows are zeros.
    data[defaults.DATA_EXCLUDE_MASK] = 0.0
    tbsum = np.sum(data, 2)
    flat = np.ravel(tbsum)

    # Loop through flat to find local maxima.
    for i in range(1, flat.size-1):
        if flat[i] > defaults.INTERESTING_THRESHOLD and flat[i-1] < flat[i] and flat[i] > flat[i+1]:
            foo, bar = np.histogram([flat[i]], bins)
            main += foo
            foo, bar = np.histogram([flat[i-1], flat[i+1]], bins)
            edges += foo

np.save('main', main)
np.save('edges', edges)
# Produce plots.
mpl.rcParams['font.size'] = 12
width = bins[1] - bins[0]
plt.bar(bins[:-1], main, width, align='edge', log=True)
# right = np.amax(bins[:-1]*(main > 1)) + 2*width
right = 4000
plt.xlim(-10, right)
plt.xlabel('Time-summed ADC Value')
plt.ylabel('Count')
plt.savefig('on_track', bbox_inches='tight')
plt.bar(bins[:-1], edges, width, align='edge', log=True)
plt.xlim(-10, right)
plt.xlabel('Time-summed ADC Value')
plt.ylabel('Count')
plt.savefig('both', bbox_inches='tight')
plt.clf()
plt.bar(bins[:-1], edges, width, align='edge', log=True)
plt.xlim(-10, right)
plt.xlabel('Time-summed ADC Value')
plt.ylabel('Count')
plt.savefig('off_track', bbox_inches='tight')
plt.clf()
plt.bar(bins[:-1], main+edges, width, align='edge', log=True)
plt.xlim(-10, right)
plt.xlabel('Time-summed ADC Value')
plt.ylabel('Count')
plt.savefig('sum', bbox_inches='tight')
