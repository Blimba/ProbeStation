"""

   Perform electroburning using the ADwin Gold ii apparatus and FEMTO DPLCA 200 Current Amplifier.

   Author: Bart Limburg
   Version: 12 July 2017

"""
from imports.adwin_femto import *
from imports.functions import add_metric_prefix, linear_fit_resistance, check_user_input
from imports.data import Data
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


def max_voltage_increase(v_max):
    return max(v_max * (1 + v_max / 20), v_max + 0.1)  # function to increase the maximum breakpoint voltage. higher increases at higher volts

def trigger_flag_to_string(flags):
    if flags & ADWIN_FLAG_BURN_OHMIC:
        return 'V overload (10 V)'
    elif flags & ADWIN_FLAG_BURN_I_OVERLOAD:
        return 'I overload'
    elif flags & ADWIN_FLAG_BURN_R_INCREASE:
        return 'large increase in R'
    elif flags & ADWIN_FLAG_BURN_R_THRESHOLD:
        return 'R larger than threshold'
    elif flags & ADWIN_FLAG_BURN_FEEDBACK:
        return 'sudden decrease in I'
    elif flags & ADWIN_FLAG_BURN_BREAKPOINT_V:
        return 'maximum V reached'

def init():
    return ADwinFemto(drain=1, source=1, iv_gain=9, burn_gain=4)

def start(instr, name, dev, **kwargs):  # This function is run for every device from main.py.
    ####################
    #  Preset globals  #
    ####################
    fail_counter = 0
    num_burn_cycles = 100
    output = []
    
    ###########################
    #  Electroburning cycles  #
    ###########################
    cont = True
    R = 1e3
    instr.burn_gain = 4

    print("Starting electroburning")
    output.append('Starting eburn')
    n = 1
    info_burn = Data(name='%s_burninfo' % name, dev = dev, coordinates='n', values=('R','breakpoint','gain', 'flags'))
    data_burn = Data(name='%s_burn' % name, dev = dev, coordinates=('Vsd','n'), values='Isd')
    data_R = Data(name='%s_R' % name, dev = dev, coordinates=('Vsd','n'), values='Isd')

    data_R.plot2d()
    data_burn.plot2d()
    bpv = 10.  # set the maximum voltage to 10 V
    if R > 1e6:
        bpv = 1.
    # loop until the electroburning is completed (R should be higher than Rcrit at the end of the process)
    Rv = 0
    Ri = 0
    while (R < R_crit and R > 0 and cont and n < num_burn_cycles):
        check_user_input()  # check for user input (asynchronously)
        # run the burning process (ElectroBurn.bas), returns the sweep data and flags
        [v, i, burn_flags] = instr.eburn(v_rate_up=kwargs.get('v_rate_up',7.6), # V/s
                                         v_rate_down=2300, # V/s
                                         max_voltage=bpv, # V
                                         feedback_high=36.6, # mI / s
                                         feedback_low=6.1, # mI / s
                                         feedback_steepness=0.6, # sigmoidal curve steepness
                                         feedback_center=1.3, # V
                                         threshold_resistance=R_crit) # Ohm

        # remember the breakpoint voltage (it is the maximum voltage from the burn cycle)
        v_max = np.max(v)
        if not (burn_flags & ADWIN_FLAG_OVERLOAD or burn_flags & ADWIN_FLAG_BURN_I_OVERLOAD or burn_flags & ADWIN_FLAG_BURN_OHMIC): # in case of overload, dont change the bpv
            if not (burn_flags & ADWIN_FLAG_UNDERLOAD and instr.burn_gain < 8): # in case of underload at lowest gain, dont change the bpv
                bpv = v_max

        # save burn data
        if np.size(v) > 1:
            data_burn.fill(v, n * np.ones(np.size(v)), np.array(i))
            data_burn.new_block()  # is this line required?
        data_burn.plot()

        # measure the new resistance between -0.1 and 0.1 V
        [v, i, _] = instr.sweep_linear(v_min=-0.4, v_max=0.4, num_datapoints=50, num_average = 10, time_per_scan=0.2)
        R = abs(linear_fit_resistance(v, i))
        info_burn.fill(n, R, v_max, instr.burn_gain, burn_flags)
        data_R.fill(v, n * np.ones(np.size(v)), i)
        data_R.new_block()
        data_R.plot()

        # output information to the user
        print('cyc %d: bpv %.2f V, R (%s) %sOhm, gain %s, tr: %s' % (n, v_max, dev, add_metric_prefix(R), instr.burn_gain, trigger_flag_to_string(burn_flags)))

        # update electroburn parameters
        n = n + 1

        # handle the burn flags
        if (auto_burn_gain):
            if (burn_flags & ADWIN_FLAG_UNDERLOAD):
                # this should be difficult to measure with current gain, change the gain!
                if (instr.burn_gain < 9):
                    instr.burn_gain += 1
                    #print('> Note: gain too low, cannot measure current. Increasing gain to: %s' % instr.burn_gain)
            elif (burn_flags & ADWIN_FLAG_OVERLOAD or burn_flags & ADWIN_FLAG_BURN_I_OVERLOAD):
                if (instr.burn_gain > 3):
                    instr.burn_gain -= 1
                    num_burn_cycles += 1
                    #print('> Note: gain too high, cannot measure current. Reducing gain to: %s' % instr.burn_gain)

        # if the burn script overloads the I or the V, stop trying after 3 times
        if (burn_flags & ADWIN_FLAG_BURN_OHMIC or (burn_flags & ADWIN_FLAG_BURN_I_OVERLOAD and instr.burn_gain == 3)):
            fail_counter = fail_counter + 1
            if (fail_counter > 2):
                print('Three fails, deserting device...')
                cont = False  # ohmic resistance found after hanging at 10 V for 5 seconds, stop burning.
        else:
            fail_counter = 0

        if (burn_flags & ADWIN_FLAG_BURN_BREAKPOINT_V):
            bpv = max_voltage_increase(bpv)
        #cont = input('Continue? (1/0): ')

    data_burn.close()
    info_burn.close()
    data_R.close()

    output.append('cycles: %s' % n)
    output.append('R: %s' % add_metric_prefix(R))
    if fail_counter > 2:
        output.append('IorV overload')
        #output.append('SKIP')
    if n == num_burn_cycles:
        output.append('repeat')  # signal user that this junction should be electroburned once more
        #output.append('SKIP')
    print("Measurement completed.")
    return output  # return the burn output to the main file. The output will be saved in a file.

def end(instr, name):
    print("Experiment concluded. It is safe to quit the application and raise the probes.")
