"""

    Measure a gate trace with a linear sweep

    Author: Bart Limburg
    Version: 12/07/2017
"""
from imports.data import Data
from imports.hp4156a import HP
from imports.adwin_femto import *
from imports.functions import sleep
import time
def init():
    return [
        ADwinFemto(drain=1, source=1, gate=2, iv_gain=9, burn_gain=4),
        HP(source=1, drain=2, gate=3, screen_refresh=False)
        ]

def get_switch_settings():
    return ('HP', 'ADWIN', 'ADWIN')

def start(instr,name, dev, **kwargs): # This function is run for every device from main.py.
    hp = instr[1]
    adwin = instr[0]
    print("Measuring Gate trace (HP) of experiment %s at device %s" % (name,dev))
    # configure the sweep
    filename = kwargs.get('filename','IVg')
    data_IVg = Data(name='%s_%s' % (name, filename), dev = dev,coordinates='Vg',values='Isd')  #create the data file
    #sleep(5)
    tm = time.time()
    adwin.current_time_trace(0.2,
                             num_average = 1000,
                             data_frequency = 50,
                             num_datapoints = 30000,
                             wait_for_complete = False,
                             in_channel = 'both')
            
    hp.sweep_triangle(v_min=-100,
                      v_max=100,
                      v_step=1,
                      electrode='gate',
                      source=0.2)
    adwin.stop() # stops the current acquisition
    [t,i,flags,_] = adwin.get_data()
    v = i[1]*10  # get the voltage applied from the hp
    i = i[0]
    data_IVg.fill(v,i)
    data_IVg.plot()
    data_IVg.close()

    print("Measurement completed at t = %d" % (time.time()-tm))

def end(instr, name):
    instr[1].zero()
