import angular_distribution
import numpy as np
import glob
import defaults
import event_plot
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

plt.rcParams.update({'font.size': 12})

def gaussian(x, A, mu, sigma, c):
    return A * np.exp(-(x-mu)**2/(2*sigma**2)) / np.sqrt(2*np.pi*sigma**2) + c

def get_com_y(evt):
    x_dim = np.arange(12)
    y_dim = np.arange(144)
    z_dim = np.arange(30)
    X, Y, Z = np.meshgrid(x_dim, y_dim, z_dim, indexing='ij')
    beta_x, beta_y, vec_func = angular_distribution.linear_fit(evt)

    neighbourhood_mask = np.logical_and(np.abs(beta_y[0] + beta_y[1] * Z - Y) <= 5, np.abs(X - np.round(vec_func(np.array([0]))[0,0])) < 1e-3)
    com_y = np.sum((evt - 9.6) * Y * neighbourhood_mask, axis=(0, 1)) / np.sum((evt - 9.6) * neighbourhood_mask, axis=(0, 1))

    return com_y, np.round(vec_func(np.array([0]))[0,0])

def plot_position_resolution(data_interesting_path = defaults.DEFAULT_INTERESTING_DATA_FOLDER + defaults.CURRENT_FILE + '/', show=True, plot_kwargs={}):
    event_files = glob.glob(data_interesting_path + '*.npy')

    bins = np.linspace(-1.5, 1.5, 100)
    print(bins)
    bin_centres = (bins + ((bins[1] - bins[0]) / 2))[:-1]
    diffs_histogram = np.zeros(bins.shape[0]-1)

    for file in event_files:
        evt = np.load(file)

        try:
            beta_x, beta_y, vec_func = angular_distribution.linear_fit(evt)
        except:
            continue

        com_y, X_fit = get_com_y(evt)
        z_dim = np.arange(30)

        has_pnt_mask = np.sum(evt * (evt > defaults.FITTING_BASELINE), axis=(0, 1)) > 0
        zs = z_dim[has_pnt_mask]
        com_y = com_y[has_pnt_mask]
        y_fit = vec_func(zs)[:,1]

        hist, bedges = np.histogram(y_fit - com_y, bins)
        diffs_histogram += hist

    plt.plot(bin_centres * defaults.DEFAULT_SPACINGS[1], diffs_histogram, **plot_kwargs)

    if show:
        plt.show()

    return bin_centres, diffs_histogram



if __name__=='__main__':
    bin_centres, diffs_histogram = plot_position_resolution(show=False, plot_kwargs={'label': 'Observed Values', 'marker': 'o', 'linestyle': 'none', 'markersize': 3})
    plt.xlabel('Centre of Mass/Charge - Fit (cm)')
    plt.ylabel('Counts')

    A = np.sum(diffs_histogram * (bin_centres[1] - bin_centres[0]))
    mu = np.sum(bin_centres * diffs_histogram) / np.sum(diffs_histogram)
    sigma = np.sqrt(np.sum(diffs_histogram * (bin_centres - mu)**2) / (np.sum(diffs_histogram)-1))

    p0 = [4000, mu, sigma, 0]

    popt, pcov = curve_fit(gaussian, bin_centres, diffs_histogram, p0=p0)
    plt.plot(bin_centres * defaults.DEFAULT_SPACINGS[1], gaussian(bin_centres, *popt), label='Gaussian Fit', linestyle='dashed', color='black')
    print('p0:', p0)
    print('popt:', popt)

    plt.legend()
    plt.show()
Footer
