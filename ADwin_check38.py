"""

    Check

    Author: Bart Limburg

"""
import numpy as np
import time
from imports.adwin_femto import *
from imports.functions import create_data_file, linear_fit_resistance, add_metric_prefix

def init(qt):
    return ADwinFemto(qt, input_channel=1, output_channel=1, iv_gain=9, burn_gain=4)

def start(qt,instr,name, dev): # This function is run for every device from main.py.
    print("Measuring R of experiment %s at device %s" % (name,dev))
    [vdat, idat, _] = instr.sweep_linear(v_min=-0.1,
                                         v_max=0.1,
                                         num_datapoints=100,
                                         time_per_scan=0.5,
                                         num_average=10,
                                         auto_gain=True)
    R = linear_fit_resistance(vdat, idat)
    print("Resistance: %sOhm" % add_metric_prefix(R))
    if R < 0 or R > 10e3:
        return (R, '%sOhm' % add_metric_prefix(R))
    return (R, '%sOhm' % add_metric_prefix(R))
