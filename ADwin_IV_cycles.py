"""

    Measure IV traces with a triangular wave

    Author: Bart Limburg

"""
import numpy as np
import time
from imports.adwin_femto import *
from imports.functions import create_data_file, linear_fit_resistance, add_metric_prefix

def init(qt):
    return ADwinFemto(qt, input_channel=1, output_channel=1, iv_gain=9, burn_gain=4)

def start(qt,instr,name, dev): # This function is run for every device from main.py.
    print("Measuring IV of experiment %s at device %s" % (name,dev))
    data_IV = create_data_file(qt,name='%s_IV_%s' % (name,dev),coordinates='Vsd',values='Isd')  #create the data file
    plot_IV = qt.Plot2D(data_IV, name='IV', coorddim=0, valdim=1, traceofs=0)
    s=time.time()
    instr.set_gain(9)
    [vdat, idat, _] = instr.sweep_triangle(v_min=-0.4,
                                           v_max=0.4,
                                           num_datapoints=400,
                                           time_per_cycle=0.1,
                                           num_cycles=50,
                                           num_average=10)

    data_IV.add_data_point(vdat,idat)
    print("Saved IV trace at time %.2f" % (time.time()-s))
        
    R = linear_fit_resistance(vdat,idat)
    
    data_IV.close_file()
    plot_IV.update()
    qt.msleep(2)
    print("Measurement completed.")
    return (R, '%sOhm' % add_metric_prefix(R))
