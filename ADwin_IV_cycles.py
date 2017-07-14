"""

    Measure IV traces with a triangular wave

    Author: Bart Limburg

"""
import time
from imports.adwin_femto import *
from imports.functions import sleep, linear_fit_resistance, add_metric_prefix
from imports.data import data

def init():
    return ADwinFemto(drain=1, source=1, iv_gain=9, burn_gain=4)

def start(instr,name, dev): # This function is run for every device from main.py.
    print("Measuring IV of experiment %s at device %s" % (name,dev))
    data_IV = data(name='%s_IV' % name, dev = dev,coordinates='Vsd',values='Isd')  #create the data file
    data_IV.plot()
    s=time.time()
    instr.set_gain(9)
    [vdat, idat, _] = instr.sweep_triangle(v_min=-0.4,
                                           v_max=0.4,
                                           num_datapoints=400,
                                           time_per_cycle=0.1,
                                           num_cycles=50,
                                           num_average=10)

    data_IV.fill(vdat,idat)
    print("Saved IV trace at time %.2f" % (time.time()-s))
        
    R = linear_fit_resistance(vdat,idat)
    
    data_IV.close()
    data_IV.plot()
    sleep(2)
    print("Measurement completed.")
    return (R, '%sOhm' % add_metric_prefix(R))
