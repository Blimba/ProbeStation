"""

    Measure IV traces with a triangular wave

    Author: Bart Limburg

"""
import numpy as np
import time
from imports.adwin_femto import *
from imports.functions import create_data_file

def init(qt):
    return ADwinFemto(qt, input_channel=1, output_channel=1, iv_gain=9, burn_gain=4)

def start(qt,instr,name, dev): # This function is run for every device from main.py.
    print("Measuring IV of experiment %s at device %s" % (name,dev))
    d=qt.Data(name='test')
    d.add_coordinate('vsd')
    d.add_value('isd')
    for i in range(1):
        instr.set_gain(9)
        [vdat, idat, _] = instr.sweep_triangle(v_min=-0.4,
                                               v_max=0.4,
                                               num_datapoints=100,
                                               time_per_cycle=0.1,
                                               num_cycles=1,
                                               num_average=1,
                                               auto_gain=False)
        d.add_data_point(vdat,idat)
        plot_IV = qt.Plot2D(d, name='test')
        plot_IV.update()
        qt.msleep(1)

    print("Measurement completed.")
