import pulse_height_spectrum
import defaults
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({'font.size': 12})

extract_drift_voltage = lambda x: x.split('-')[1].split('_')[0]

anode_1500 = ['2010_101_+1500_-1100_34k_0403', '2010_101_+1500_-1200_30k_0407', '2010_101_+1500_-1300_30k_0406', '1910_101_+1500_-1400_38k_0387', '2010_101_+1500_-1500_36k_0405', '2010_101_+1500_-1600_30k_0404']
anode_1400 = ['1910_101_+1400_-1100_30k_0393', '2010_101_+1500_-1100_34k_0403', '1910_101_+1400_-1400_31k_0402', '1910_101_+1400_-1300_9k_0395', '1910_101_+1400_-1500_30k_0400']
drift_const = ['1910_101_+1500_-1400_38k_0387', '2210_101_+1433_-1400_30k_0410', '2210_101_+1466_-1400_30k_0412', '1910_101_+1400_-1400_31k_0402']

files = anode_1500
files.sort(key=extract_drift_voltage)

drift_voltages = []
sums = []

for file in files:
    drift_voltage = extract_drift_voltage(file)
    interesting_data_folder = defaults.DEFAULT_INTERESTING_DATA_FOLDER + file + '/'
    phs = pulse_height_spectrum.plot_pulse_height(interesting_data_folder, show=False, plot_kwargs={'label': 'Drift Voltage: -' + str(drift_voltage) + 'V'})

    drift_voltages.append(drift_voltage)
    sums.append(np.sum(phs))

print(list(zip(drift_voltages, sums)))

plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
plt.xlabel('Time (seconds)')
plt.ylabel('Average ADC value')
plt.legend()
plt.show()
Footer
© 2022
