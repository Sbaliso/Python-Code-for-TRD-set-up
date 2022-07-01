import matplotlib.pyplot as plt
import numpy as np
import glob
import defaults
import adcarray as adc
import o32reader as rdr
import angular_distribution
import event_plot

plt.rcParams.update({'font.size': 12})

def plot_pulse_height(interesting_data_folder = defaults.DEFAULT_INTERESTING_DATA_FOLDER + defaults.CURRENT_FILE + '/', show=True, plot_kwargs={}):
    t_axis = np.arange(defaults.NUMBER_OF_TIME_BINS) * defaults.TIME_RESOLUTION
    pulse_height_sum = np.zeros(defaults.NUMBER_OF_TIME_BINS)

    x_dim = np.arange(12)
    y_dim = np.arange(144)
    z_dim = np.arange(30)
    X, Y, Z = np.meshgrid(x_dim, y_dim, z_dim, indexing='ij')

    event_files = glob.glob(interesting_data_folder+'*.npy')
    sample_count = np.zeros(30)
    for evno, file in enumerate(event_files):
        evt = np.load(file)

        if evno % defaults.PRINT_EVNO_EVERY == 0:
            print("Proccessing events %d - %d" % (evno, evno + defaults.PRINT_EVNO_EVERY))

        evt[evt < 100] = 0.0

        try:
            beta_x, beta_y, vec_func = angular_distribution.linear_fit(evt, threshold=defaults.FITTING_BASELINE)
            adjacent_mask = np.logical_and(np.abs(beta_y[0] + beta_y[1] * Z - Y) <= 2.5, np.abs(X - np.round(vec_func(np.array([0]))[0,0])) < 1e-3)
            sample_count[list(set(np.where(adjacent_mask)[2]))] += 1
        except np.linalg.linalg.LinAlgError as e:
            print(repr(e))
            continue
        evt[~adjacent_mask] = 0
        pulse_height_sum += np.sum(evt, axis=(0,1))

    pulse_height_spectrum = pulse_height_sum / sample_count

    plt.plot(t_axis, pulse_height_spectrum, **plot_kwargs)
    if show:
        plt.show()
    return pulse_height_spectrum

if __name__=='__main__':
    plot_pulse_height(show=False, plot_kwargs={'label': 'Anode Voltage: +1500V. Drift Voltage: -1400V.'})
    plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    plt.xlabel('Time since trigger (seconds)')
    plt.ylabel('Average ADC value')
    plt.legend()
    plt.show()
