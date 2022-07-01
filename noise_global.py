from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import scipy.special as sp
import numpy as np
import glob
import defaults
import matplotlib
from scipy.optimize import curve_fit
matplotlib.rcParams.update({'font.size': 18})
matplotlib.rcParams['text.usetex'] = True
matplotlib.rcParams['text.latex.unicode'] = True

plotdir = 'plots/'

if __name__=='__main__':
    interesting_data_folder = defaults.DEFAULT_INTERESTING_DATA_FOLDER + defaults.CURRENT_FILE + '/'
    event_files = glob.glob(interesting_data_folder+'*.npy')
    globmean_t = []
    gbsqmean_t = []
    for file in event_files:
        filename = file.split('/')[-1].split('.')[0]
        event_num = int(filename.split('_')[0])
        evt = np.load(file)
        evt_sq = np.array([x*x for x in evt])
        points_tot = np.prod(evt.shape)
        globmean_t.append(evt.sum(axis=(0,1,2))/points_tot)
        gbsqmean_t.append(evt_sq.sum(axis=(0,1,2))/points_tot)
MEAN = np.array(globmean_t)
STANDEV = np.sqrt(np.array(gbsqmean_t)-MEAN**2)

plt.rcParams["patch.force_edgecolor"] = True
plt.figure(figsize=(8,6))
plt.grid()
plt.xlabel('$\mu_G(e)$')
plt.ylabel('Frequency')
#plt.title('Histogram of $\mu(e)$')
#mu = np.mean(NOISE)
vals, binedges = np.histogram(MEAN, bins='fd')
bins = (binedges[:-1]+binedges[1:])/2

def gaussian(x,A,sig,mu):
    return (A/(sig*np.sqrt(2*np.pi))*np.exp(-0.5*((x-mu)**2/sig**2)))

cond = (bins>=9.45)&(bins<9.8)
x = bins[cond]
y = vals[cond]
u = np.sqrt(y)+0.0001
p0 = np.array([31, 1.4, 9.5])
[A0, sig0, mu0] = p0
name = ['A', 'sigm', 'mu']
tmodel = np.linspace(min(x),max(x),1000)
ystart = gaussian(tmodel,*p0)
popt, pcov = curve_fit(gaussian,x,y,p0,sigma=u,absolute_sigma=True)
dymin = (y -gaussian(x,*popt))/u       #vectorised again
min_chisq = sum(dymin**2)
dof = len(x) - len(popt)                #number of degrees of freedom

print('Chi square:',min_chisq)
print('Number of degrees of freedom:',dof)
print('Chi square per degree of freedom:',
min_chisq/dof, '\n')

print('Fitting parameters with 68% C.I.:')

for i,pmin in enumerate(popt):
    print('%2i %-10s %12f +/- %10f'%(i+1,
    name[i],pmin,np.sqrt(pcov[i,i])*np.sqrt(min_chisq/dof)),
     '\n')

perr = np.sqrt(np.diag(pcov))
print(perr, '\n')

yfit = gaussian(tmodel,*popt)
plt.errorbar(x, y, u,0,'.',color='steelblue',label="Data Points")
plt.plot(tmodel,yfit,'--k', label='Best fit')
plt.legend()
param_name = ['$C$','$\sigma$','$\mu$']
for i in range(3):
    print("%s & %.2f \pm %.2f"%(param_name[i],popt[i],perr[i]))
plt.savefig(plotdir+'noise_glob_mn.png')
plt.show()
"""
plt.figure(figsize=(8,6))
plt.grid()
plt.xlabel('$\sigma(e)$')
plt.ylabel('Frequency')
plt.title('Histogram of $\sigma(e)$')
#mu = np.mean(NOISE)
vals, binedges = np.histogram(STANDEV, bins='auto')
bins = (binedges[:-1]+binedges[1:])/2
plt.errorbar(bins, vals, np.sqrt(vals),0,'k.')
#plt.legend()
plt.savefig(plotdir+'noise_glob_sd.png')
plt.show()
"""
