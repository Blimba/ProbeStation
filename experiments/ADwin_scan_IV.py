"""

    Measure IV traces with a triangular wave

    Author: Bart Limburg

"""
from imports.adwin_femto import *
from imports.data import Data
from imports.functions import sleep

def init():
    return ADwinFemto(drain=1, source=1, iv_gain=9, burn_gain=4)

def start(instr,name, dev): # This function is run for every device from main.py.
    print("Measuring IV of experiment %s at device %s" % (name,dev))
    d=Data(name='%s_IV' % name, dev = dev, coordinates='Vsd', values='Isd')
    d.plot()
    instr.iv_gain = 9
    [v, i, flags] = instr.sweep_linear(v_min=-0.4,
                                       v_max=0.4,
                                       num_datapoints=100,
                                       time_per_scan=10,
                                       num_average=15000,
                                       auto_gain=True,
                                       )
    d.fill(v,i)
    d.plot()
    d.save_png()
    d.close()
    print("Measurement completed.")
