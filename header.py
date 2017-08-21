# This file is imported from main.py
import os
import re
import inspect
import time
qtlab_dir = os.getcwd()  # the qtlab folder.
script_dir =  os.path.dirname(inspect.getabsfile(lambda x: 0))  # use a little cheat to get the script path.
try: os.chdir(script_dir)
except: raise SystemError("Error: Script directory not found! This is kind of impossible.")
from imports.chip import Chip
from imports.experiment import Experiment
from imports.cascade import Cascade
from imports.arduino import SignalSwitch
from imports.functions import *
import imports.data as d
reload(d)
d.basepath = '%s%s\\%s' % (d.basepath, time.strftime('%Y'), script_dir.split('\\')[-1])
try: os.chdir(qtlab_dir)
except: raise SystemError("Error: QTLab directory not found! This is also kind of impossible.")
os.chdir(script_dir)

# give the experiment name. This is used in all data files
try:
    tname = raw_input("Experiment codename (%s)? " % name)
    name = tname if tname else name
except:
    name = raw_input("Experiment codename? ")
try:
    if subdir:
        tsubdir = raw_input("Subdirectory (%s\\%s)? " % (d.basepath, subdir))
        subdir = tsubdir if tsubdir else subdir
    else:
        subdir = raw_input("Subdirectory (%s\\subdir?)? " % d.basepath)
except:
    subdir = raw_input("Subdirectory (%s\\subdir?)? " % d.basepath)
if subdir:
    d.basepath = '%s\\%s\\%s' % (d.basepath, name, subdir)
else:
    d.basepath = '%s\\%s' % (d.basepath, name)