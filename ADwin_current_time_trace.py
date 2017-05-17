"""

    Perform a current versus time trace using the ADwin Gold ii apparatus
    and the FEMTO DPLCA 200 Current Amplifier.

    Author: Bart Limburg

"""
import numpy as np
import time
from imports.adwin_femto import *
from imports.functions import create_data_file

def init(qt):
    return ADwinFemto(qt, input_channel=1, output_channel=1, iv_gain=9, burn_gain=4)

def start(qt,instr,name, dev): # This function is run for every device from main.py.
    print("Measuring IT-trace of experiment %s at device %s" % (name,dev))
    data_IV = create_data_file(qt,name='%s_IV_%s' % (name,dev),coordinates='time',values='Isd')
    plot_IV = qt.Plot2D(data_IV, name='IT', coorddim=0, valdim=1, traceofs=0)
    s=time.time()
    for j in range(1):
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
            data_IV.add_data_point(t,i)
            plot_IV.update()
        
        print("Saved IV trace at time %.2f" % (time.time()-s))

    data_IV.close_file()
    print("Measurement completed.")
