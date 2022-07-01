from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import scipy.special as sp
import numpy as np
import glob
import defaults
import matplotlib
matplotlib.rcParams.update({'font.size': 18})
matplotlib.rcParams['text.usetex'] = True
matplotlib.rcParams['text.latex.unicode'] = True

plotdir = 'plots/'

if __name__=='__main__':
    interesting_data_folder = defaults.DEFAULT_INTERESTING_DATA_FOLDER + defaults.CURRENT_FILE + '/'
    event_files = glob.glob(interesting_data_folder+'*.npy')
    padmean_t = np.zeros((12,144))
    psqmean_t = np.zeros((12,144))
    no_of_evt = 0
    for file in event_files:
        filename = file.split('/')[-1].split('.')[0]
        event_num = int(filename.split('_')[0])
        evt = np.load(file)
        evt_sq = np.array([x*x for x in evt])
        psqmean_t += np.sum(evt_sq, axis=2)/evt.shape[2]
        padmean_t += np.sum(evt, axis=2)/evt.shape[2]
        no_of_evt +=1

E_psq = psqmean_t/no_of_evt
E_pad = padmean_t/no_of_evt
standev = np.sqrt(E_psq-(E_pad)**2)
detector_dimensions=defaults.DEFAULT_DETECTOR_DIMENSIONS
x_dim = np.linspace(0, detector_dimensions[0], evt.shape[0])
y_dim = np.linspace(0, detector_dimensions[1], evt.shape[1])
x_dim = np.array(range(evt.shape[0]+1))
y_dim = np.array(range(evt.shape[1]+1))
X, Y = np.meshgrid(x_dim, y_dim, indexing='ij')

print(str(defaults.CURRENT_FILE))
plt.figure(figsize=(8,6))
plt.pcolor(X, Y, standev, vmin=0.8, vmax=2.2)
plt.colorbar()
#plt.title('$\sigma(r,c)$')
plt.xlabel('Row')
plt.ylabel('Column')
plt.savefig(plotdir+'noise_pad_sd.png')
plt.show()

plt.figure(figsize=(8,6))
plt.pcolor(X, Y, E_pad)#, vmin=8.5, vmax=10.5)
#plt.title(title)
plt.colorbar()
#plt.title('$\mu(r,c)$')
plt.xlabel('Row')
plt.ylabel('Column')
plt.savefig(plotdir+'noise_pad_mn.png')
plt.show()
