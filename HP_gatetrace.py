"""

    Measure a gate trace with a linear sweep

    Author: Bart Limburg
    Version: 12/07/2017
"""
from imports.data import data
from imports.hp4156a import HP

def init():
    return HP()

def start(instr,name, dev): # This function is run for every device from main.py.
    print("Measuring Gate trace (HP) of experiment %s at device %s" % (name,dev))
    # configure the sweep

    data_IVg = data(name='%s_IVg' % name, dev = dev,coordinates='Vg',values='Isd')  #create the data file

    instr.write(0.2,electrode='source')
    [v,i] = instr.sweep_triangle(v_min=-50,v_max=100,v_step=1,electrode='gate')
    instr.write(0.0, electrode='source')

    data_IVg.fill(v,i)
    data_IVg.plot()
    data_IVg.close()

    print("Measurement completed.")

def end(instr, name):
    instr.zero()
