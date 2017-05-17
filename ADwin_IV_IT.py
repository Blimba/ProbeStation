"""

    Measure IV traces with a triangular wave

    Author: Bart Limburg

"""
import numpy as np
import time
from imports.adwin_femto import *
from imports.functions import *

def init(qt):
    return ADwinFemto(qt, input_channel=1, output_channel=1, iv_gain=9, burn_gain=4)

def start(qt,instr,name, dev): # This function is run for every device from main.py.
    s=time.time()
    [v, i, _] = instr.sweep_linear(v_min=-0.1, v_max=0.1, num_datapoints=50, num_average=10, time_per_scan=0.1)
    R = linear_fit_resistance(v, i)
    print("Resistance of device %s: %s" % (dev, add_metric_prefix(R)))
    if True: #R > 1e6 and R < 1e10:
        print("Measuring IV of experiment %s at device %s" % (name,dev))
        data_IV = create_data_file(qt,name='%s_IV_%s' % (name,dev),coordinates='Vsd',values='Isd')  #create the data file
        data_IT = create_data_file(qt,name='%s_IT_%s' % (name,dev),coordinates='t',values='Isd')  #create the data file
        data_IT2 = create_data_file(qt,name='%s_IT2_%s' % (name,dev), coordinates='t', values='Isd')
        plot_IV = qt.Plot2D(data_IV, name='IV', coorddim=0, valdim=1, traceofs=0)
        plot_IT = qt.Plot2D(data_IT, name='IT', coorddim=0, valdim=1, traceofs=0)
        plot_IT2 = qt.Plot2D(data_IT2, name='IT2', coorddim=0, valdim=1, traceofs=0)

        instr.set_gain(9)
        [vdat, idat, _] = instr.sweep_triangle(v_min=-0.4,
                                               v_max=0.4,
                                               num_datapoints=400,
                                               time_per_cycle=0.1,
                                               num_cycles=50,
                                               num_average=10)

        data_IV.add_data_point(vdat,idat)
        plot_IV.update()
        print("Saved IV trace at time %.2f" % (time.time()-s))
        instr.write(0.4)
        qt.msleep(0.5)
        print("Measuring IT trace...")
        [t, i, flags] = instr.current_time_trace(v=0.1,
                                                 num_datapoints=6000,
                                                 data_frequency=100,
                                                 num_average=10,
                                                 wait_for_complete=False)

        # because wait_for_complete is false, we can plot (incomplete) data until the data_incomplete flag is cleared
        data_start=0
        while(flags & ADWIN_FLAG_DATA_INCOMPLETE):  # the data incomplete flag is only set when the measurement is still ongoing
            qt.msleep(0.5)
            try:
                [t,i,flags,data_start] = instr.get_data(data_start)
                data_IT.add_data_point(t,i)
                plot_IT.update()
            except: pass
        print("Saved IT trace at time %.2f" % (time.time()-s))
        [t, i, flags] = instr.current_time_trace(v=0.1,
                                                 num_datapoints=50000,
                                                 data_frequency=10000,
                                                 num_average=1)
        data_IT2.add_data_point(t,i)
        plot_IT2.update()
        
        data_IV.close_file()
        data_IT.close_file()
        data_IT2.close_file()
    print("Measurement completed.")
    return [R]
    
