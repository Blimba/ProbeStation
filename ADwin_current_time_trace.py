"""

    Perform a current versus time trace using the ADwin Gold ii apparatus
    and the FEMTO DPLCA 200 Current Amplifier.

    Author: Bart Limburg

"""
import numpy as np
import time
from imports.adwin_femto import *
from imports.data import data

def init():
    return ADwinFemto(drain=1, source=1, iv_gain=9, burn_gain=4)

def start(instr, name, dev): # This function is run for every device from main.py.
    print("Measuring IT-trace of experiment %s at device %s" % (name,dev))
    data_IT = data(name='%s_IT' % name, dev=dev, coordinates='time',values='Isd')
    s=time.time()
    [t, i, flags] = instr.current_time_trace(v=0.4,
                                             num_datapoints=300,
                                             data_frequency=10,
                                             num_average=50,
                                             wait_for_complete=False)

    # because wait_for_complete is false, we can plot (incomplete) data until the data_incomplete flag is cleared
    data_start=0
    while(flags & ADWIN_FLAG_DATA_INCOMPLETE):  # the data incomplete flag is only set when the measurement is still ongoing
        qt.msleep(0.5)
        [t,i,flags,data_start] = instr.get_data(data_start)
        data_IT.fill(t,i)
        data_IT.plot()  #updates plot if it exists

    print("Saved IV trace at time %.2f" % (time.time()-s))

    data_IT.close_file()
    print("Measurement completed.")
