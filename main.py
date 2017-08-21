#
#   Modular Probe Station Script
#
#   Author: Bart Limburg
#   Version: 21 August 2017
#
#   Usage:
#
#       This script file takes care of automated movement over devices.
#       For every device, 1 or more script files are called (explained below)
#
#       The script can import a file with a list of devices to loop over.
#       A csv file should be supplied. For example: a1,b2,g6
#       This would loop over those 3 devices. However, also ranges can be supplied
#       For example: a,c-e,f30-h3 would perform the entire column a (from the minimum row to the maximum row, defined below)
#       followed by the entire columns c, d and e. Lastly, it loops over devices f30 to the maximum number in column f,
#       do the entire column g, then from the minimum row of column h, to h3.
#       Lastly, supply * to loop over all devices on the defined chip.
#
#       More explanation can be found in the chip.py documentation
#
#       The actual experiment code is found in different scripts, and is run by the main script on the devices that are
#       defined in the code below in the user configurable part.
#
#       Your experiment script should have two basic functions:
#
#       def init():
#           In this function, define the instrument(s) that you will use. For example:
#           return qt.instruments.create('femto_dlpca_200','FEMTO_DLPCA_200',dev=1)
#           It is possible to return multiple devices, or perform other actions in this function
#
#       def start(instr,name,dev):
#           This function is called by the main script for every device over which it loops.
#           The instrument(s) returned by the init function are passed to the function.
#           In addition, the experiment name "name" and the current device "dev" are also passed.
#           This function is the heart of the script. Perform whatever you want to do for each device here.
#           For example, measure your IVtraces, perform electroburning, electroannealing, or whatever.
#           Optionally, the function may return a (list of) value(s) that will be saved in an expinfo file.
#           If you return the word "STOP" (or the word you set in the user customisable section below) the experiment
#           will stop automated movement and quit the application.
#
#       optionally, your script may contain the following function:
#
#       def end(instr,name):
#           This function is called after all devices have been looped over. Your instruments and the experiment name are passed to the function.
#           If your instruments require a shutdown command (or you want to terminate other things), do so here.
#
execfile("header.py")
#################################
#                               #
#   USER CUSTOMISABLE SECTION   #
#                               #
#################################

# load the chip object
chip = Chip(name=name,template='2T.ini',ignore_hidden=False)

# load the signal switch. Does signal switching automatically based on the name of the script file. Be careful: starting your scriptname with HP will make the signal switch to HP!
signal_switch = SignalSwitch()  
    
#chip.limit_range('a1-k18')  # use this to cut up a standard design chip into quarters

# load the devices that should run on the current chip. Device ranges are treated by COLUMNS. i.e.:
# 'a' -> run the entire column a (as defined in the template)
# 'a-c' -> run the entire columns a, b and c
# 'b3-6' -> run column b from row 3 to 6 (i.e., b3, b4, b5 and b6)
# 'b15-c3' -> run column b from row 15 until the end of the column (as defined in the template), and column c from the beginning until c3.
# you may define multiple ranges by comma seperation (i.e., 'a3-5, b6, f').
# you may run a device multiple times: 'a1,a1'
chip.load_devices('o21-w')

# alternatively, load the devices from a csv file (given the same syntax as defined above)
# chip.load_from_file('exp_devices.csv')

# add experiments to the chip. The device ranges are treated as SQUARES. So: b3-c4 includes devices b3, b4, c3 and c4.
chip.add_experiment("ADwin_resistance")  # the resistance script outputs a 'SKIP' if the resistance is too low or too high, in which case the other experiments are skipped
chip.add_experiment("ADwin_electroburn",'a1-w37')
chip.add_experiment("ADwin_IV_cycles",'a1-w37')


exp_stop_code = 'STOP'  # if this word is output by an experiment, the main script halts
exp_skip_code = 'SKIP'  # if this word is output by an experiment, the remaining experiments are skipped and the next device will run.
exp_run_code = 'RUN'  # if this word is output by an experiment, it will run the experiment that it output next in the outputlist (e.g., return ['RUN','ADwin_IV_cycles',dev])

# load the saved position of the cascade (set to False to input the current position if you moved the cascade manually)
load_saved_position = False

# start from the current position of cascade (set to false to start from the beginning of the list)
start_at_current_position = False

# if run_skipped_devices is set to true, and the current position of the cascade is not on the beginning of the list
# then we would go back to the beginning of the list after completing it. Otherwise, we stop at the end of the list
# for example, we are running column b, but the cascade is currently at device b3. When set to true,
# we would go from b3 to the end of the column, and then run b1 and b2. When set to false, b1 and b2 are not run.
run_skipped_devices = False

# when return_to_start is set to True, the cascade moves back to the starting device after completing the exp
return_to_start = False

# safety for the probes, will ask the user if the probes are in contact
probe_contact_safety = True

#########################################
#                                       #
#   END OF USER CUSTOMISABLE SECTION    #
#                                       #
#########################################

# ask the user for the position of the probes
execfile("position.py")

# run the experiments
execfile("run_experiments.py")

