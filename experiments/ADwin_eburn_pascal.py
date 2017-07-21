"""

   Perform electroburning using the ADwin Gold ii apparatus and FEMTO DPLCA 200 Current Amplifier.

   Author: Bart Limburg
   Version: 10/02/2017

"""
import numpy as np
from imports.adwin_femto import *
from imports.functions import add_metric_prefix, linear_fit_resistance, create_data_file
import qt
# critical resistance at which the junction is considered a tunneling junction
R_crit = 500e6

# IV trace (after burning) settings
v_start = -0.4
v_stop = 0.4
datapoints = 400
scan_time = 1
cycles = 10

# burning settings
auto_burn_gain = True  # for autogaining between L3 and L4 (required for broader graphene junctions)
num_burn_cycles = 60

def max_voltage_increase(v_max):
    return v_max * min(1 + v_max / 20, 1.05)  # function to increase the maximum breakpoint voltage. higher increases at higher volts

def init():
    return ADwinFemto(input_channel=1, output_channel=1, iv_gain=9, burn_gain=4)

def start(instr, name, dev):  # This function is run for every device from main.py.
    ####################
    #  Preset globals  #
    ####################
    ohmflag_counter = 0
    output = []
    ##########################################
    #  Measure the resistance of the device  #
    ##########################################)
    # do a quick sweep to measure the resistance between -0.1 and 0.1 V
    [v, i, _] = instr.sweep_linear(v_min=-0.4, v_max=0.4, num_datapoints=50, num_average=25, time_per_scan=0.5)
    
    R = linear_fit_resistance(v, i)
    print("R of device %s = %sOhm" % (dev, add_metric_prefix(R)))
    
    ###########################
    #  Electroburning cycles  #
    ###########################
    cont = True
    instr.burn_gain = 4
    if (R > 10 and R < R_crit and R > 0 and cont):  # if R is a good value, create the burning file.
        print("Starting electroburning")
        output.append('Starting eburn')
        n = 1
        diff = 1
        info_burn = create_data_file(name='%s_burninfo_%s' % (name, dev), coordinates='n', values=('R','breakpoint','gain'))
        data_burn = create_data_file(name='%s_burn_%s' % (name, dev), coordinates=('Vsd','n'), values='Isd')
        
        plot_burn = qt.Plot2D(data_burn, name='burn current', coorddim=0, valdim=2, traceofs=0)
        bpv = 10.  # set the maximum voltage to 10 V
        # loop until the electroburning is completed (R should be higher than Rcrit at the end of the process)
        while (R < R_crit and R > 0 and cont and n < num_burn_cycles):
            # run the burning process (ElectroBurn.bas), returns the sweep data and flags
            [v, i, burn_flags] = instr.burn(n, ramp_up=0.5, ramp_down=150,
                                            max_voltage=max_voltage_increase(bpv),
                                            sigmoid_high=25,
                                            sigmoid_low=5,
                                            sigmoid_steepness=0.8,
                                            sigmoid_center=2.0,
                                            process_delay=30000)
            # remember the breakpoint voltage (it is the maximum voltage from the burn cycle)
            if not (burn_flags & ADWIN_FLAG_OVERLOAD):
                bpv = np.max(v)
            # save burn data
            if np.size(v) > 1:
                data_burn.add_data_point(v, n * np.ones(np.size(v)), np.array(i))
                data_burn.new_block()  # is this line required?
            plot_burn.update()
            # measure the new resistance between -0.1 and 0.1 V
            [v, i, _] = instr.sweep_linear(v_min=-0.1, v_max=0.1, num_datapoints=50, num_average = 10, time_per_scan=0.1)
            R = linear_fit_resistance(v, i)
            info_burn.add_data_point(n, R, bpv, instr.burn_gain)

            
            # output information to the user
            print('R (%s) = %sOhm, %d cycles, breakpoint = %.2f V, gain = 10^%s' % (dev, add_metric_prefix(R), n, bpv, instr.burn_gain))

            # update electroburn parameters
            n = n + 1
            diff = 4

            # handle the burn flags: underload, overload and ohmic junction flag
            if (auto_burn_gain):
                if (burn_flags & ADWIN_FLAG_UNDERLOAD):
                    # this should be difficult to measure with current gain, change the gain!
                    if (instr.burn_gain < 4):
                        instr.burn_gain += 1
                        print('> Note: gain too low, cannot measure current. Increasing gain to: %s' % instr.burn_gain)
                elif (burn_flags & ADWIN_FLAG_OVERLOAD):
                    if (instr.burn_gain > 3):
                        instr.burn_gain -= 1
                        print('> Note: gain too high, cannot measure current. Reducing gain to: %s' % instr.burn_gain)
                    else:
                        print("> Device too conductive, deserting...")
                        cont=False

            # if 10 V does not electroburn the junction, then stop trying after 3 tries.
            if (burn_flags & ADWIN_FLAG_BURN_OHMIC):
                print('> Device burned at 10 V for 5 seconds, junction too ohmic.')
                ohmflag_counter = ohmflag_counter + 1
                if (ohmflag_counter > 2):
                    print('Three fails, deserting device...')
                    cont = False  # ohmic resistance found after hanging at 10 V for 5 seconds, stop burning.
            else:
                ohmflag_counter = 0
            if R < 1e4:
                bpv = 10                
        data_burn.close_file()
        info_burn.close_file()
        output.append('cycles: %s' % n)
        output.append('R: %s' % add_metric_prefix(R))
        if ohmflag_counter > 2:
            output.append('too ohmic')
        if n == 60:
            output.append('repeat')  # signal user that this junction should be electroburned once more
        #############################################################
        #  Measure an IV trace after electroburning has terminated  #
        #############################################################
        print("Measuring IV of experiment " + name + " at device " + dev)
        data_IV = create_data_file(name='%s_IV_%s' % (name, dev), coordinates='Vsd', values='Isd')
        plot_IV = qt.Plot2D(data_IV, name='IV', coorddim=0, valdim=1, traceofs=0)
        instr.iv_gain = 9
        [vdat, idat, _] = instr.sweep_triangle(v_min=v_start,
                                               v_max=v_stop,
                                               num_datapoints=datapoints,
                                               time_per_cycle=scan_time,
                                               num_cycles=cycles)
        data_IV.add_data_point(vdat, idat)
        data_IV.close_file()
        plot_IV.update()
    print("Measurement completed.")
    return output  # return the burn output to the main file. The output will be saved in a file.

def end(instr, name):
    print("Experiment concluded. It is safe to quit the application and raise the probes.")
