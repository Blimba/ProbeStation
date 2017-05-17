"""

    Measure a gate trace with a linear sweep

    Author: Bart Limburg
    Version: 10/02/2017

"""
import numpy as np
import time
from imports.adwin_femto import *
from imports.functions import *

def init(qt):
    return ADwinFemto(qt, input_channel=1, output_channel=1, iv_gain=9, burn_gain=4)

def start(qt,instr,name, dev): # This function is run for every device from main.py.
    print("Measuring Gate trace of experiment %s at device %s" % (name,dev))
    data_IV = create_data_file(qt,name='%s_IVg_%s' % (name,dev),coordinates='Vg',values='Isd')  #create the data file
    plot_IV = qt.Plot2D(data_IV, name='IVg', coorddim=0, valdim=1, traceofs=0)
    s=time.time()
    for i in range(1):
        instr.write(0.1,electrode='source') # apply a source-drain bias voltage (the source electrode can be omitted as it is the standard setting, but for clarity it is included here)
        [vdat, idat, _] = instr.sweep_linear(v_min=-10,
                                             v_max=10,
                                             electrode='gate',
                                             num_datapoints=2000,
                                             scan_rate=5,
                                             num_average=50)

        data_IV.add_data_point(vdat,idat)
        print("Saved gate trace at time %.2f" % (time.time()-s))

    plot_IV.update()
    data_IV.close_file()
    print("Measurement completed.")
