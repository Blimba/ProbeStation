"""

    Measure a gate trace with a linear sweep

    Author: Bart Limburg
    Version: 12/07/2017

"""
import time
from imports.adwin_femto import *
from imports.data import data

def init():
    return ADwinFemto(drain=1, source=1, gate=2, iv_gain=9, burn_gain=4)

def start(instr,name, dev): # This function is run for every device from main.py.
    print("Measuring Gate trace of experiment %s at device %s" % (name,dev))
    data_IVsVg = data(name='%s_IVsVg' % name, dev = dev, coordinates=('Vg','Vsd'), values='Isd')  #create the data file
    t = time.time()
    min = -3
    max = 3
    step = 0.1
    vgs = np.arange(min,max+step,step)
    if vgs[0] < 0:
        for vg in np.arange(0,vgs[0],-0.1):
            instr.write(vg,electrode='gate')
    elif vgs[0] > 0:
        for vg in np.arange(0,vgs[0],0.1):
            instr.write(vg,electrode='gate')
    for vg in vgs:
        instr.write(vg,electrode='gate') # apply a source-drain bias voltage (the source electrode can be omitted as it is the standard setting, but for clarity it is included here)
        [v, i, _] = instr.sweep_linear(v_min=-.4,
                                             v_max=.4,
                                             num_datapoints=400,
                                             time_per_scan=0.1,
                                             num_average=10)
        #instr.write(0.0,electrode='source')
        data_IVsVg.fill(Vsd = v, Vg = vg*np.ones(len(v)), Isd = i)
        data_IVsVg.new_block()
    data_IVsVg.plot()
    data_IVsVg.close()
    print("Measurement completed in %.2f seconds." % (time.time()-t))
