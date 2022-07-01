from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import glob
import defaults

def plot_event(evt, detector_dimensions=defaults.DEFAULT_DETECTOR_DIMENSIONS, plot_threshold=defaults.DEFAULT_PLOT_BASELINE, title='', show=True):
    x_dim = np.linspace(0, detector_dimensions[0], evt.shape[0])
    y_dim = np.linspace(0, detector_dimensions[1], evt.shape[1])
    z_dim = np.linspace(0, -detector_dimensions[2], evt.shape[2])
    X, Y, Z = np.meshgrid(x_dim, y_dim, z_dim, indexing='ij')

    muon_mask = evt > plot_threshold
    evt[np.logical_not(muon_mask)] = 0

    fig = plt.figure()
    cmhot = plt.cm.get_cmap("hot")
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlim(0, detector_dimensions[0])
    ax.set_ylim(0, detector_dimensions[1])
    ax.set_zlim(-detector_dimensions[2], 0)
    ax.plot_wireframe(X[:,:,0], Y[:,:,0], Z[:,:,0])
    ax.plot_wireframe(X[:,:,-1], Y[:,:,-1], Z[:,:,-1])
    p = ax.scatter(X[muon_mask], Y[muon_mask], Z[muon_mask], c=evt[muon_mask].flatten(), cmap = cmhot)
    #p = ax.scatter(X, Y, Z, c=evt.flatten(), s=evt.flatten(), cmap = cmhot)
    plt.colorbar(p)
    plt.title(title)

    if show:
        plt.show()

    return ax

if __name__=='__main__':
    interesting_data_folder = defaults.DEFAULT_INTERESTING_DATA_FOLDER + defaults.CURRENT_FILE + '/'
    event_files = glob.glob(interesting_data_folder+'*.npy')
    for file in event_files:
        filename = file.split('/')[-1].split('.')[0]
        event_num = int(filename.split('_')[0])
        evt = np.load(file)
        plot_event(evt, title='Event ' + str(event_num) + '. Max ADC value: ' + str(np.max(evt)))
