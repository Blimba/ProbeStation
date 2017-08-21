"""

    Measure a gate trace with a linear sweep

    Author: Bart Limburg
    Version: 12/07/2017
"""
from imports.data import Data
from imports.hp4156a import HP
from imports.functions import sleep

def init():
    return HP(source=1, drain=2, gate=3, screen_refresh=False)

def start(instr,name, dev): # This function is run for every device from main.py.
    print("Measuring Gate trace (HP) of experiment %s at device %s" % (name,dev))
    # configure the sweep

    data_IVg = Data(name='%s_IVg' % name, dev = dev,coordinates='Vg',values='Isd')  #create the data file

    [v,i] = instr.sweep_triangle(v_min=-50,v_max=100,v_step=1,electrode='gate',source=0.2)


    data_IVg.fill(v,i)
    data_IVg.plot()
    data_IVg.close()

    print("Measurement completed.")

def end(instr, name):
    instr.zero()
