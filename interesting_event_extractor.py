#!/usr/bin/env python3
#450 spike at event 617
#703 spike at event 1858
import adcarray as adc
import pylab as pl
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import os
import defaults
import glob
import o32reader as rdr

def adc_threshold(data, threshold = defaults.INTERESTING_THRESHOLD):
    return np.max(data) > threshold

def adc_threshold_and_single_row(data, threshold = defaults.INTERESTING_THRESHOLD):
    return adc_threshold(data) and len(set(np.where(data > threshold / 3)[0])) == 1

data_is_interesting = adc_threshold_and_single_row

def extract_interesting_events(data_folder = defaults.DEFAULT_DATA_FOLDER, filename=defaults.CURRENT_FILE, threshold = defaults.INTERESTING_THRESHOLD, interesting_output_directory = defaults.DEFAULT_INTERESTING_DATA_FOLDER):
    reader = rdr.o32reader(data_folder + filename)
    analyser = adc.adcarray()

    output_dir = interesting_output_directory + filename + '/'

    try:
        os.makedirs(output_dir)
        print('Output directory created.')
    except FileExistsError:
        print('Output directory already exists.')

    maxevno = None
    minevno = None
    absmax = None
    absmin = None
    for evno, raw_data in enumerate(reader):
        if evno % defaults.PRINT_EVNO_EVERY == 0:
            print("Proccessing events %d - %d" % (evno, evno + defaults.PRINT_EVNO_EVERY))

        if evno == 0:
            continue        #Skip first event (may be a configuration event depending on run configurations).

        try:
            analyser.analyse_event(raw_data)
        except adc.datafmt_error as e:
            print(repr(e))
            continue
        data = analyser.data[:12]           #Last four rows are zeros. (Ask Dittel).
        data[defaults.DATA_EXCLUDE_MASK] = 0.0

        maxval = np.max(data)
        minval = np.min(data)

        if absmax is None or maxval > absmax:
            absmax = maxval
            maxevno = evno

        if absmin is None or minval < absmin:
            absmin = minval
            minevno = evno

        if data_is_interesting(data, threshold):
            output_file = output_dir + str(evno) + '_thresh_' + str(threshold) + '.npy'
            print("Found interesting data. Saving to", output_file, ' max value ', np.max(data))
            np.save(output_file, data)

    print("Max value", absmax, 'obtained in event', maxevno)
    print("Min value", absmin, 'obtained in event', minevno)

if __name__=='__main__':
    extract_interesting_events()

    # fils = glob.glob(defaults.DEFAULT_DATA_FOLDER+'/*')
    # for fil in fils:
    #     extract_interesting_events(filename=fil.split('/')[1])
Footer
© 2022
