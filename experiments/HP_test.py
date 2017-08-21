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

    sleep(30)
    print("Measurement completed.")

def end(instr, name):
    instr.zero()
