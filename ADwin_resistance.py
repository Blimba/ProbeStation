"""

    Measures resistance, outputs the resistance and if the resistance is not within range, skip the rest of the experiments

    Author: Bart Limburg
    Version: 12/07/2017

"""
from imports.adwin_femto import *
from imports.functions import linear_fit_resistance, add_metric_prefix

def init():
    return ADwinFemto(drain=1, source=1, iv_gain=9, burn_gain=4)

def start(instr,name, dev): # This function is run for every device from main.py.
    print("Measuring R of experiment %s at device %s" % (name,dev))
    [vdat, idat, _] = instr.sweep_linear(v_min=-0.4,
                                         v_max=0.4,
                                         num_datapoints=100,
                                         time_per_scan=0.2,
                                         num_average=10,
                                         auto_gain=True)
    R = linear_fit_resistance(vdat, idat)
    print("Resistance: %sOhm" % add_metric_prefix(R))
    if R < 0 or R > 5e8:
        return (R, '%sOhm' % add_metric_prefix(R), 'SKIP') # resistance not in range, skip next experiments
    return (R, '%sOhm' % add_metric_prefix(R))
