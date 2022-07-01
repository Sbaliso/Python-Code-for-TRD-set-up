import glob
from event_plot import plot_event
from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt
import defaults

def lin_func(X, beta):
    return X.dot(beta)

def linear_fit_1D(x, y, weights):
    X = np.ones((x.shape[0], 2))
    X[:, 1] = x
    X = weights.reshape((-1,1)) * X
    beta = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(weights * y)
    return beta

def linear_fit(evt, threshold=defaults.FITTING_BASELINE):
    interaction_mask = evt > threshold
    pnts = np.where(interaction_mask)
    X_inds, Y_inds, Z_inds = pnts
    weights = evt[X_inds, Y_inds, Z_inds] - 9.6
    beta_x = linear_fit_1D(Z_inds, X_inds, weights)
    beta_y = linear_fit_1D(Z_inds, Y_inds, weights)

    def vec_func(Z):
        pnts = np.zeros((Z.shape[0], 2))
        pnts[:,0] = beta_x[0] + beta_x[1] * Z
        pnts[:,1] = beta_y[0] + beta_y[1] * Z
        return pnts
    return beta_x, beta_y, vec_func

def convert_betas_to_angles(beta_x, beta_y, detector_spacings=defaults.DEFAULT_SPACINGS):
    mx = beta_x[1] * detector_spacings[0] / detector_spacings[2]
    my = beta_y[1] * detector_spacings[1] / detector_spacings[2]
    theta = np.arccos(1/np.sqrt(mx**2 + my**2 + 1))# - np.pi/2
    phi = np.arctan(my / mx) + np.pi/2 + (mx < 0) * np.pi
    return np.asarray([theta, phi])

def get_angular_distribution(data_path, threshold = defaults.FITTING_BASELINE, detector_dimensions = defaults.DEFAULT_DETECTOR_DIMENSIONS, detector_spacings=defaults.DEFAULT_SPACINGS, show_plots=False):
    event_files = glob.glob(data_path+'*.npy')

    angles = np.zeros((len(event_files), 2))
    for index, file in enumerate(event_files):
        if index % defaults.PRINT_EVNO_EVERY == 0:
            print("Proccessing interesting events %d - %d" % (index, index + defaults.PRINT_EVNO_EVERY))
        filename = file.split('/')[-1].split('.')[0]
        event_num = int(filename.split('_')[0])
        evt = np.load(file)

        try:
            beta_x, beta_y, vec_func = linear_fit(evt, threshold=threshold)
            angs = convert_betas_to_angles(beta_x, beta_y, detector_spacings=detector_spacings)
            angles[index] = angs
            # if angs[0] > 1.5 / 2:
            #     show_plots = True
            # else:
            #     show_plots = False
            #print('beta_x:', beta_x, 'beta_y:', beta_y, 'theta:', angs[0], 'phi:', angs[1])
        except Exception as e:
            print('UNABLE TO LINEAR FIT. Error:', repr(e))
            if show_plots:
                plot_event(evt, title='UNABLE TO LINEAR FIT')
            angles[index] = np.nan
            continue

        if show_plots:
            print(beta_x, beta_y, angs[0])
            z_dim = np.arange(30)
            X_fit, Y_fit = vec_func(z_dim).T
            ax = plot_event(evt, detector_dimensions=detector_dimensions, show=False)
            print(X_fit * detector_spacings[0], Y_fit * detector_spacings[1], -z_dim * detector_spacings[2])
            ax.plot(X_fit * detector_spacings[0], Y_fit * detector_spacings[1], -z_dim * detector_spacings[2], color='green')
            plt.show()

    return angles

def sphere_embed(coords):
    theta, phi = coords
    return np.asarray([np.sin(theta) * np.sin(phi), np.sin(theta) * np.cos(phi), np.cos(theta)])

def spherical_plot(angles):
    coordinate_angles = np.meshgrid(np.linspace(0, np.pi/2, 100), np.linspace(0, 2*np.pi, 100))

    X, Y, Z = sphere_embed(angles.T)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_wireframe(*sphere_embed(coordinate_angles), cstride=10, rstride=10, linewidth=0.5)
    ax.scatter(X, Y, Z, color='red', marker='o', s=3)
    plt.show()

if __name__=='__main__':
    interesting_data_folder = defaults.DEFAULT_INTERESTING_DATA_FOLDER + defaults.CURRENT_FILE + '/'
    angles = get_angular_distribution(interesting_data_folder, show_plots=False)
    print(np.max(angles))
    print(np.nanmin(angles, axis=0))
    print(np.nanmax(angles, axis=0))
    print(angles.shape)
    spherical_plot(angles)

    theta, phi = angles.T

    plt.hist(theta[~np.isnan(theta)] * 360 / (2*np.pi), bins=50)
    plt.xlabel('Inclination Angle (Degrees)')
    plt.ylabel('Counts')
    plt.show()
