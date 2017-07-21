"""

    Measure a gate trace with a linear sweep

    Author: Bart Limburg
    Version: 12/07/2017

"""
from imports.adwin_femto import *
from imports.data import Data

def init():
    return ADwinFemto(drain=1, source=1, iv_gain=9, burn_gain=4)

def start(instr,name, dev): # This function is run for every device from main.py.
    print("Measuring Gate trace (ADwin) of experiment %s at device %s" % (name,dev))
    data_IVg = Data(name='%s_IVg' % name, dev = dev, coordinates='Vg', values='Isd')  #create the data file

    instr.write(0.1,electrode='source') # apply a source-drain bias voltage (the source electrode can be omitted as it is the standard setting, but for clarity it is included here)
    [vdat, idat, _] = instr.sweep_triangle(v_min=-2,
                                           v_max=2,
                                           electrode='gate',
                                           num_datapoints=400,
                                           time_per_cycle=1,
                                           num_cycles=5,
                                           num_average=10)
    instr.write(0.0,electrode='source')

    data_IVg.fill(vdat,idat)
    data_IVg.close()
    data_IVg.plot()
    print("Measurement completed.")
