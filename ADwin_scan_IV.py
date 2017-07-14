"""

    Measure IV traces with a triangular wave

    Author: Bart Limburg

"""
from imports.adwin_femto import *
from imports.data import data

def init():
    return ADwinFemto(drain=1, source=1, iv_gain=9, burn_gain=4)

def start(instr,name, dev): # This function is run for every device from main.py.
    print("Measuring IV of experiment %s at device %s" % (name,dev))
    d=data(name='%s_IV' % name, dev = dev, coordinates='Vsd', values='Isd')
    d.plot()
    instr.iv_gain = 9
    [vdat, idat, _] = instr.sweep_triangle(v_min=-0.4,
                                           v_max=0.4,
                                           num_datapoints=100,
                                           time_per_cycle=0.1,
                                           num_cycles=1,
                                           num_average=1,
                                           auto_gain=True)
    d.fill(vdat,idat)
    d.plot()
    print("Measurement completed.")
