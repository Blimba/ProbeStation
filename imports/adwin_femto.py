"""

Driver for interfacing the ADWin Gold II with the FEMTO DPLCA 200 current to voltage converter

Author: Bart Limburg (supporting scripts: Xinya Bian, Jan Mol)
Version: 2 June 2017

Setting up the hardware:
    Connect the ADwin output 1 (or any of your choosing, see below) to probe 1
    Connect probe 2 to the FEMTO input
    Set the FEMTO gain to remote
    Connect FEMTO output to ADwin input 1 (or any of your choosing, see below)
    In case of a third electrode to gate, connect ADwin output 2 (or any of your choosing, see below) to gate probe
    Correctly ground the FEMTO housing to a common ground.

Driver initialisation:
    instrument = ADwinFemto()  # loads the instrument with standard parameters
        possible parameters to edit:
        input_channel = 1  # change to the ADwin ADC channel of your choosing
        output_channel = 1  # change to the ADwin DAC channel of your choosing
        gate_channel = 2  # change to the ADwin DAC gate channel of your choosing
        iv_gain = 9  # order of magnitude of original gain (10^9 is the standard setting, which corresponds to L9.)
        burn_gain = 4  # order of magnitude of the burn_gain (10^4 is the standard setting, which corresponds to L4.)
    Calling this function loads the ADwin and FEMTO instruments
    Additionally, 5 processes will be loaded:
        C:\scripts\ADwin\Standard\DAC.bas  # for simple DAC conversion (writing)
        C:\scripts\ADwin\Standard\ADC.bas  # for simple ADC conversion (reading)
        C:\scripts\ADwin\Standard\Sweep_Linear.bas  # for a (single) linear sweep iv trace
        C:\scripts\ADwin\Standard\Sweep_Triangle.bas  # for triangular wave voltammetry
        C:\scripts\ADwin\Standard\ElectroBurn.bas  # for feedback controlled electroburning

Driver usage:
    outputting a voltage:
        instrument.write(voltage)  # this function will run the DAC.bas script that outputs a voltage on the output channel
        instrument.write_gate(voltage)  # this function will run the DAC.bas script that outputs a voltage on the gate channel

    reading a voltage:
        instrument.read(auto_gain = True)  # this function returns the current flowing through the FEMTO at the input channel
            parameters:
                auto_gain = True if the user wants to let the computer decide the gain for the FEMTO. Setting it to
                    False will collect the data even if it is overloaded or underloaded
    voltammetry:
        instrument.sweep_linear(self,v_min,v_max,num_datapoints=100, scan_rate=-1, time_per_scan=-1, scan_frequency=1, num_average=1, auto_gain = True)
            Runs the Sweep_Linear.bas script
            parameters:
                v_min = the starting voltage at which to begin the sweep
                v_max = the ending voltage at which the sweep is ended
                num_datapoints = the total amount of datapoints between v_min and v_max (including v_min and v_max)
                scan_rate = the speed at which the voltage is changed in units of V/s
                time_per_scan = the total time 1 scan will take
                scan_frequency = the frequency at which to scan
                    !!!Only one of the above three parameters (scan_rate, time_per_scan or scan_frequency) should be set
                    by the user, as from the set value, the other two will be calculated!!!
                num_average = the number of averaged reads per voltage (this does not increase measurement time)
                auto_gain = True if the user wants to let the computer decide the gain for the FEMTO. Setting it to
                    False will collect the data even if it is overloaded or underloaded
            returns: [v,i,flags]
                v = a numpy array of voltage with a length of num_datapoints
                i = a numpy array of current with a length of num_datapoints (the gain is automatically taken into account)
                flags = a bitarray of flags. ANDing versus the flags ADWIN_FLAG_UNDERLOAD or ADWIN_FLAG_OVERLOAD in the following way:
                    if (flags & ADWIN_FLAG_UNDERLOAD):
                        the currect was too low to correctly measure with the set gain values (auto_gain is preferably used)
                    if (flags & ADWIN_FLAG_OVERLOAD):
                        the currect was too high to correctly measure with the set gain values (auto_gain is preferably used)

        instrument.sweep_triangle(self, v_min, v_max, v_start=0, num_datapoints=200, scan_rate=-1., time_per_cycle=-1., cycle_frequency=1, num_average=1, num_cycles=1, auto_gain = True)
            Runs the Sweep_Triangle.bas script
            parameters:
                v_min = the minimum (left-side) voltage at which to change sweep direction
                v_max = the maximum (right-side) voltage at which to change sweep direction
                v_start = the starting voltage at which to begin the sweep
                num_datapoints = the total amount of datapoints per cycle
                scan_rate = the speed at which the voltage is changed in units of V/s
                time_per_cycle = the total time 1 cycle will take
                cycle_frequency = the frequency at which to scan cycles
                    !!!Only one of the above three parameters (scan_rate, time_per_scan or scan_frequency) should be set
                    by the user, as from the set value, the other two will be calculated!!!
                num_average = the number of averaged reads per voltage (this does not increase measurement time)
                num_cycles = the number of cycles to scan (these scans are just appended to the data file)
                auto_gain = True if the user wants to let the computer decide the gain for the FEMTO. Setting it to
                    False will collect the data even if it is overloaded or underloaded
            returns: [v,i,flags]
                v = a numpy array of voltage with a length of num_datapoints * num_cycles
                i = a numpy array of current with a length of num_datapoints * num_cycles (the gain is automatically taken into account)
                flags = a bitarray of flags. ANDing versus the flags ADWIN_FLAG_UNDERLOAD or ADWIN_FLAG_OVERLOAD in the following way:
                    if (flags & ADWIN_FLAG_UNDERLOAD):
                        the currect was too low to correctly measure with the set gain values (auto_gain is preferably used)
                    if (flags & ADWIN_FLAG_OVERLOAD):
                        the currect was too high to correctly measure with the set gain values (auto_gain is preferably used)

        instrument.burn(self, cycle_num, differential = 1, ramp_up = 0.5, ramp_down = 150, max_voltage = 10)
            Runs the ElectroBurn.bas script
            parameters:
                cycle_num = the current cycle number of the electroburning. This affects some parameters in the ElectroBurn.bas script
                differential, ramp_up and ramp_down are probably better left untouched.
                max_voltage = the maximum voltage that should be ramped too. In order to not overburn the graphene junctions
                    this value should be corrected for by the user each cycle.
            returns:
                v = a numpy array of voltage with a length of num_datapoints * num_cycles
                i = a numpy array of current with a length of num_datapoints * num_cycles (the gain is automatically taken into account)
                flags = a bitarray of flags. ANDing versus the flags ADWIN_FLAG_UNDERLOAD or ADWIN_FLAG_OVERLOAD in the following way:
                    if (flags & ADWIN_FLAG_UNDERLOAD):
                        the currect was too low to correctly measure with the set gain values (there is no auto_gain for burning!)
                    if (flags & ADWIN_FLAG_OVERLOAD):
                        the currect was too high to correctly measure with the set gain values (there is no auto_gain for burning!)
                    if (flags & ADWIN_FLAG_BURN_OHMIC):
                        The script went all the way to 10 V and stayed there for 5 seconds without the junction breaking,
                        the junction is too conductive and probably will not burn.
"""
import qt
import numpy as np

ADWIN_FLAG_OVERLOAD             = int('0000000000000001',2)
ADWIN_FLAG_UNDERLOAD            = int('0000000000000010',2)
ADWIN_FLAG_DATA_INCOMPLETE      = int('0000000000000100',2)
ADWIN_FLAG_NO_DATA              = int('0000000000001000',2)
ADWIN_FLAG_ERROR                = int('1000000000000000',2)
# Burn trigger flags
ADWIN_FLAG_BURN_OHMIC           = int('0000000000010000',2) # 16
ADWIN_FLAG_BURN_R_INCREASE      = int('0000000000100000',2) # 32
ADWIN_FLAG_BURN_R_THRESHOLD     = int('0000000001000000',2) # 64
ADWIN_FLAG_BURN_FEEDBACK        = int('0000000010000000',2) # 128
ADWIN_FLAG_BURN_I_OVERLOAD      = int('0000000100000000',2) # 256
ADWIN_FLAG_BURN_BREAKPOINT_V    = int('0000001000000000',2) # 512

BUFFER_SIZE = 8e6
PROCESS_CLOCK = 300e6  # PROCESS CLOCK OF THE ADWIN
PROCESSDELAY_MINIMUM = 1000
_UNDERLOAD_THRESHOLD = 0.95
_OVERLOAD_THRESHOLD = 9.5

class ADwinFemto(object):
    loaded=False
    def __init__(self, drain=1, source=1, gate = 2, iv_gain = 9, burn_gain = 4):
        if not ADwinFemto.loaded:
            ADwinFemto._adwin = qt.instruments.create('adwin_gold_ii', 'ADwin_Gold_II', dev=1)
            # self._adwin.boot()
            ADwinFemto._femto = qt.instruments.create('femto_dlpca_200', 'FEMTO_DLPCA_200', dev=1)
            ADwinFemto._adwin.load_process(self._adwin.compile_process('C:\scripts\ADwin\Standard\DAC.bas', process=1))
            ADwinFemto._adwin.load_process(self._adwin.compile_process('C:\scripts\ADwin\Standard\ADC.bas', process=2))
            ADwinFemto._adwin.load_process(self._adwin.compile_process('C:\scripts\ADwin\Standard\Sweep_Linear.bas', process=3))
            ADwinFemto._adwin.load_process(self._adwin.compile_process('C:\scripts\ADwin\Standard\Sweep_Triangle.bas', process=4))
            ADwinFemto._adwin.load_process(self._adwin.compile_process('C:\scripts\ADwin\Standard\ElectroBurnNew.bas', process=5))
            ADwinFemto._adwin.load_process(self._adwin.compile_process('C:\scripts\ADwin\Standard\ITTrace.bas', process=6))
            ADwinFemto.loaded=True
        self._adwin = ADwinFemto._adwin
        self._femto = ADwinFemto._femto
        self.set_input_channel(drain)
        self.set_output_channel(source)
        self.set_gate_channel(gate)
        self.iv_gain = iv_gain
        self.burn_gain = burn_gain
        self._busy_par = 'par20' # initial busy parameter (just so that we don't crash)
        self._iv_gain_list = ['','','','L3','L4','L5','L6','L7','L8','L9']
            

    def set_input_channel(self, channel):
        self._input_channel = channel

    def set_output_channel(self, channel):
        self._output_channel = channel

    def set_gate_channel(self, channel):
        self._gate_channel = channel

    def set_gain(self,gain):
        try:
            self._femto.set('gain',self._iv_gain_list[gain])
        except:
            self._femto.set('gain',gain)

    def _voltage_to_digit(self, v):
        return int(65535 / 20.0 * (v + 10.0))

    def _digit_to_voltage(self, d):
        return (d * 20.0 / 65535 - 10.0)

    def is_busy(self):
        return self._adwin.get(self._busy_par)

    def _auto_gain_iv(self,r,electrode='source'):
        successful = False
        while not successful:
            # set adwin parameters to measure a single fast sweep
            if electrode == 'gate':
                self._adwin.set('par21', self._gate_channel)
            else:
                self._adwin.set('par21', self._output_channel)
            self._adwin.set('par22', self._input_channel)
            self._adwin.set('par23', self._voltage_to_digit(r[0]))
            self._adwin.set('par24', self._voltage_to_digit(r[1]))
            self._adwin.set('par25', (self._voltage_to_digit(r[1])-self._voltage_to_digit(r[0])) / 9)
            self._adwin.set('par26', 5000)
            self._adwin.set('par27', 5)
            self._adwin.set('par28', 10)
            
            self.write(r[0],electrode=electrode)
            self._adwin.start_process(3)  # run the sweep_linear program
            while self._adwin.get('par30'): pass  # wait while the adwin program is busy
            count = self._adwin.get('par29')  # count the data
            i = np.array(self._adwin.get('data2')[:(count)]) * (20.0 / 65535) - 10.0                      
            if (np.max(np.absolute(i)) > _OVERLOAD_THRESHOLD):
                if self._iv_gain_list[self.iv_gain-1] != '':
                    self.iv_gain -= 1
                    self.set_gain(self.iv_gain)
                else:
                    successful = True
            elif (np.max(np.absolute(i)) < _UNDERLOAD_THRESHOLD):
                try:
                    _ = self._iv_gain_list[self.iv_gain+1]
                    self.iv_gain += 1
                    self.set_gain(self.iv_gain)
                except:
                    successful = True
            else:
                successful = True
            #print("autogained to 10^%d" % self.iv_gain)

    def write_gate(self,v):
        self._adwin.set('par1', self._gate_channel)
        self._adwin.set('par2', self._voltage_to_digit(v))
        self._adwin.start_process(1)

    def write(self,v,electrode='source'):
        if electrode == 'gate':
            self._adwin.set('par1', self._gate_channel)
        else:
            self._adwin.set('par1', self._output_channel)
        self._adwin.set('par2', self._voltage_to_digit(v))
        self._adwin.start_process(1)

    def read(self, auto_gain = True):
        self._adwin.set('par11', self._input_channel)
        self._adwin.set('par19', 50)  # this is the number of datapoints to be averaged. hardcoded could be changed.
        successful = False
        i=0
        while not successful:
            self._busy_par = 'par20'
            self.set_gain(self.iv_gain)
            self._adwin.start_process(2)
            while self._adwin.get(self._busy_par): pass  # wait until done
            i = self._digit_to_voltage(self._adwin.get('par11'))
            if not auto_gain:
                successful = True
            else:
                if (abs(i) > _OVERLOAD_THRESHOLD):
                    if self._iv_gain_list[self.iv_gain-1] != '':
                        self.iv_gain -= 1
                    else:
                        successful = True
                elif (abs(i) < _UNDERLOAD_THRESHOLD):
                    try:
                        _ = self._iv_gain_list[self.iv_gain+1]
                        self.iv_gain += 1
                    except:
                        successful = True
                else:
                    successful = True
        return i*(10**(-self.iv_gain))

    def get_data(self,start=0):
        flag = 0
        if self.is_busy():
            flag |= ADWIN_FLAG_DATA_INCOMPLETE
        if self._busy_par == 'par30' or self._busy_par == 'par50':  # sweeps
            count = self._adwin.get('par29')  # get the data count
            v = np.array(self._adwin.get('data1')[start:(count - 1)]) * (20.0 / 65535) - 10.0  # get voltage digit and transform into real units
            i = np.array(self._adwin.get('data2')[start:(count - 1)]) * (20.0 / 65535) - 10.0  # get current digit transform into real units
            # in case autogain was not used, flags can still identify under/overloading
            if not v.size and not i.size:
                flag |= ADWIN_FLAG_NO_DATA
            if np.max(np.absolute(i)) < _UNDERLOAD_THRESHOLD:
                flag |= ADWIN_FLAG_UNDERLOAD
            elif np.max(np.absolute(i)) > _OVERLOAD_THRESHOLD:
                flag |= ADWIN_FLAG_OVERLOAD
            return [v,i*(10**(-self.iv_gain)), flag, count]
        elif self._busy_par == 'par60':  # current versus time
            count = self._adwin.get('par57')  # get the data count
            clock = self._adwin.get('par54')
            t = np.array(self._adwin.get('data1')[start:count]) * (clock/PROCESS_CLOCK)  # get voltage digit and transform into real units
            i = np.array(self._adwin.get('data2')[start:count]) * (20.0 / 65535) - 10.0  # get current digit transform into real units
            if not t.size and not i.size:
                flag |= ADWIN_FLAG_NO_DATA
            if np.max(np.absolute(i)) < _UNDERLOAD_THRESHOLD:
                flag |= ADWIN_FLAG_UNDERLOAD
            elif np.max(np.absolute(i)) > _OVERLOAD_THRESHOLD:
                flag |= ADWIN_FLAG_OVERLOAD
            return [t, i*(10**(-self.iv_gain)), flag, count]
        elif self._busy_par == 'par40':  # electroburning
            count = self._adwin.get('par39')  # get the amount of datapoints
            v = np.array(self._adwin.get('data1')[:count]) * (20.0 / 65535) - 10.0  # get voltage digit and transform into real units
            i = np.array(self._adwin.get('data2')[:count]) * (20.0 / 65535) - 10.0  # get current digit transform into real units
            flag = self._adwin.get('par37')  # get the burn flags
            if not v.size and not i.size:
                flag |= ADWIN_FLAG_NO_DATA
            if np.max(np.absolute(i)) < _UNDERLOAD_THRESHOLD:
                flag |= ADWIN_FLAG_UNDERLOAD
            elif np.max(np.absolute(i)) > _OVERLOAD_THRESHOLD:
                flag |= ADWIN_FLAG_OVERLOAD
            return [v, i*(10**(-self.burn_gain)), flag, count]
        else:
            return [[],[],ADWIN_FLAG_NO_DATA | ADWIN_FLAG_ERROR,0]

    def sweep_linear(self,v_min,v_max,num_datapoints=100, electrode = 'source', scan_rate=-1, time_per_scan=-1,
                     scan_frequency=1,  num_average=1, auto_gain = True, wait_for_complete = True):
        
        if (num_datapoints > BUFFER_SIZE):
            print("Warning: possible data overflow of ADWin Gold II hardware.")
        if (num_datapoints < 4):
            print("Error: measuring less than 4 datapoints per linear line is not allowed")
            return [[],[],ADWIN_FLAG_NO_DATA | ADWIN_FLAG_ERROR]
        v_min = float(v_min)
        v_max = float(v_max)
        self.set_gain(self.iv_gain)
        if auto_gain:
            self._auto_gain_iv((v_min,v_max),electrode=electrode)  # sets the gain to be able to record the iv trace
            
        v_bias = v_max - v_min
        if scan_rate > 0:  # scan_rate is in V/s
            time_per_scan = v_bias/scan_rate  # in seconds
            scan_frequency = 1/time_per_scan  # in Hertz
        elif time_per_scan > 0:
            scan_frequency = 1/time_per_scan
            scan_rate = v_bias/time_per_scan
        elif scan_frequency > 0:
            time_per_scan = 1/scan_frequency
            scan_rate = v_bias / time_per_scan
        # set the output and input channels to those set in the class
        if electrode == 'gate':
            self._adwin.set('par21' , self._gate_channel)
        else:
            self._adwin.set('par21', self._output_channel)
        self._adwin.set('par22' , self._input_channel)
        # set the range and stepsize of the measurement
        self._adwin.set('par23' , self._voltage_to_digit(v_min))
        self._adwin.set('par24' , self._voltage_to_digit(v_max))
        # there are num_datapoints-1 steps to do in a linear sweep, set the correct stepsize
        self._adwin.set('fpar25' , float(self._voltage_to_digit(v_max)-self._voltage_to_digit(v_min))/float(num_datapoints-1))
        # set the process delay
        processdelay = int(PROCESS_CLOCK * time_per_scan / (num_datapoints*num_average))
        if processdelay < PROCESSDELAY_MINIMUM:
            print("Warning: attempting to measure too fast, decrease scan_rate, num_datapoints, or num_average.")
        self._adwin.set('par26', processdelay)
        # set the number of averaging
        self._adwin.set('par27', num_average)
        # set the number of datapoints to measure
        self._adwin.set('par28', num_datapoints)
        # preset the starting voltage
        self.write(v_min,electrode=electrode)
        self._busy_par = 'par30'
        self._adwin.start_process(3)  # run the sweep_linear program
        if wait_for_complete:
            while self._adwin.get(self._busy_par): pass  # wait while the adwin program is busy
            v = np.array(self._adwin.get('data1')[:num_datapoints]) * (20.0 / 65535) - 10.0
            i = np.array(self._adwin.get('data2')[:num_datapoints]) * (20.0 / 65535) - 10.0
            # in case autogain was not used, flags can still identify under/overloading
            flag = 0
            if not v.size and not i.size:
                flag |= ADWIN_FLAG_NO_DATA
            if np.max(np.absolute(i)) < _UNDERLOAD_THRESHOLD:
                flag |= ADWIN_FLAG_UNDERLOAD
            elif np.max(np.absolute(i)) > _OVERLOAD_THRESHOLD:
                flag |= ADWIN_FLAG_OVERLOAD
            return [v,i*(10**(-self.iv_gain)),flag]
        else:
            return [[],[],ADWIN_FLAG_DATA_INCOMPLETE | ADWIN_FLAG_NO_DATA]


    def sweep_triangle(self, v_min, v_max, v_start=0, num_datapoints=200, electrode = 'source', scan_rate=-1.,
                       time_per_cycle=-1., cycle_frequency=1, num_average=1, num_cycles=1, auto_gain = True,
                       wait_for_complete = True):
        if (num_datapoints*num_cycles > BUFFER_SIZE):
            print("Warning: possible data overflow of ADWin Gold II hardware.")
        if (num_datapoints < 10):
            print("Error: measuring less than 10 datapoints per cycle is not allowed")
            return [[], [], ADWIN_FLAG_NO_DATA | ADWIN_FLAG_ERROR]
        v_min = float(v_min)
        v_max = float(v_max)
        if(v_start < v_min or v_start > v_max):
            print("Error: v_start is not in the bias window.")
            return [[],[],ADWIN_FLAG_NO_DATA | ADWIN_FLAG_ERROR]
        self.set_gain(self.iv_gain)
        if auto_gain:
            self._auto_gain_iv((v_min,v_max),electrode=electrode)  # sets the gain to be able to record the iv trace
        self.write(v_start,electrode=electrode)  # output the starting voltage
        if electrode == 'gate':
            self._adwin.set('par41', self._gate_channel)
        else:
            self._adwin.set('par41', self._output_channel)
        self._adwin.set('par42' , self._input_channel)
        v_bias = v_max-v_min
        if scan_rate > 0:  # scan_rate is in V/s
            time_per_cycle = 2 * v_bias/scan_rate  # in seconds
            cycle_frequency = 1/time_per_cycle  # in Hertz
        elif time_per_cycle > 0:
            cycle_frequency = 1/time_per_cycle
            scan_rate = 2 * v_bias/time_per_cycle
        elif cycle_frequency > 0:
            time_per_cycle = 1/cycle_frequency
            scan_rate = 2 * v_bias / time_per_cycle
        # set the process delay
        processdelay = int(PROCESS_CLOCK * time_per_cycle / (num_datapoints*num_average))
        if processdelay < PROCESSDELAY_MINIMUM:
            print("Warning: attempting to measure too fast, decrease scan_rate, num_datapoints, or num_average.")
        self._adwin.set('par43', processdelay)
        # set the voltages
        self._adwin.set('par44', self._voltage_to_digit(v_min))
        self._adwin.set('par45', self._voltage_to_digit(v_max))
        self._adwin.set('par46', self._voltage_to_digit(v_start))
        # set the step size based on the number of data points and maximum bias
        self._adwin.set('fpar41', ((2*v_bias)/(num_datapoints-2))*(65535/20))
        # set the number of cycles the script takes
        self._adwin.set('par47', num_cycles)
        # set the number of averaging
        self._adwin.set('par48', num_average)
        # start the process
        self._busy_par = 'par50'
        self._adwin.start_process(4)
        if wait_for_complete:
            while self._adwin.get(self._busy_par): pass
            count = self._adwin.get('par49')
            v =  np.array(self._adwin.get('data1')[:count]) * (20.0 / 65535) - 10.0
            i =  np.array(self._adwin.get('data2')[:count]) * (20.0 / 65535) - 10.0
            # in case autogain was not used, flags can still identify under/overloading
            flag = 0
            if not v.size and not i.size:
                flag |= ADWIN_FLAG_NO_DATA
            if np.max(np.absolute(i)) < _UNDERLOAD_THRESHOLD:
                flag |= ADWIN_FLAG_UNDERLOAD
            elif np.max(np.absolute(i)) > _OVERLOAD_THRESHOLD:
                flag |= ADWIN_FLAG_OVERLOAD
            return [v,i*(10**(-self.iv_gain)),flag]
        else:
            return [[],[],ADWIN_FLAG_DATA_INCOMPLETE | ADWIN_FLAG_NO_DATA]

    def eburn(self, v_rate_up = 7.5, v_rate_down = 1, max_voltage = 10, hold_at_10 = 1, feedback_high = 24,
              feedback_low = 4, feedback_center = 1.5, feedback_steepness = 0.8, threshold_resistance = 1e9,
              process_delay=3000, wait_for_complete = True):
        '''
        runs a cycle of electroburning for the adwin

        :param v_rate_up: upwards rate in V/s
        :param v_rate_down: downwards rate in V/s
        :param max_voltage: maximum applied voltage in V
        :param hold_at_10: time to hold at the highest possible voltage
        :param feedback_high: feedback parameter high value (at low voltage)
        :param feedback_low:  feedback parameter low value (at high voltage)
        :param feedback_center: center voltage for switch between high and low with a sigmoidal curve
        :param feedback_steepness: steepness of the feedback parameter switch between high and low
        :param threshold_resistance: threshold resistance at which to trigger
        :param wait_for_complete: wait for the process to complete before proceeding, or proceed with python code while the adwin is busy
        :return: tuple of V data, I data and flags

        adwin communication parameters:
        pc >> adwin
        Par_31 = input channel
        Par_32 = output channel
        Par_33 = maximum voltage (triggers)
        Par_34 = hold counter at 10 V
        Par_35 = process delay
        FPar31 = ramp up (digits/processdelay)
        FPar32 = ramp down (digits/processdelay)
        FPar33 = fb high
        FPar34 = fb low
        FPar35 = fb center
        FPar36 = fb steepness
        FPar37 = burn gain (in powers)
        FPar38 = threshold resistance (triggers)

        adwin >> pc
        Par_40 = busy? 1 = process running, 0 = done
        Par_39 = num datapoints
        Par_38 = trigger type
        '''

        self.set_gain(self.burn_gain)
        # change the sigmoidal functions
        feedback_high *= 10 ** (self.burn_gain - 4)
        feedback_low *= 10 ** (self.burn_gain - 4)
        # set the required parameters for the script
        self._adwin.set('par31', self._input_channel)
        self._adwin.set('par32', self._output_channel)
        self._adwin.set('par33', self._voltage_to_digit(max_voltage))
        self._adwin.set('par34', hold_at_10 / (process_delay / PROCESS_CLOCK))
        self._adwin.set('par35', process_delay)  # process delay
        self._adwin.set('fpar31', (v_rate_up * (65535 / 20)) * (process_delay / PROCESS_CLOCK))
        self._adwin.set('fpar32', (v_rate_down * (65535 / 20)) * (process_delay / PROCESS_CLOCK))
        self._adwin.set('fpar33', feedback_high)
        self._adwin.set('fpar34', feedback_low)
        self._adwin.set('fpar35', feedback_center)
        self._adwin.set('fpar36', feedback_steepness)
        self._adwin.set('fpar37', 10 ** self.burn_gain)
        self._adwin.set('fpar38', threshold_resistance)
        self._busy_par = 'par40'
        self._adwin.start_process(5)
        if wait_for_complete:
            while self._adwin.get(self._busy_par): pass  # test the busy parameter until adwin is finished one cycle
            count = self._adwin.get('par39')  # get the amount of datapoints
            v = np.array(self._adwin.get('data1')[:count]) * (20.0 / 65535) - 10.0  # get voltage digit and transform into real units
            i = np.array(self._adwin.get('data2')[:count]) * (20.0 / 65535) - 10.0  # get current digit transform into real units
            slope = np.array(self._adwin.get('data3')[:count])
            flag = self._adwin.get('par38')  # get the burn flags
            if not v.size and not i.size:
                flag |= ADWIN_FLAG_NO_DATA
            if np.max(np.absolute(i)) < _UNDERLOAD_THRESHOLD:
                flag |= ADWIN_FLAG_UNDERLOAD
            elif np.max(np.absolute(i)) > _OVERLOAD_THRESHOLD:
                flag |= ADWIN_FLAG_OVERLOAD
            return [v, i * (10 ** (-self.burn_gain)), flag, slope]
        else:
            return [[], [], ADWIN_FLAG_DATA_INCOMPLETE | ADWIN_FLAG_NO_DATA, []]

    def burn(self, cycle_num, ramp_up = 0.5, ramp_down = 150, max_voltage = 10, hold_at_10 = 5, process_delay = 18000,
             sigmoid_center = 1.5, sigmoid_steepness = 0.8, sigmoid_high = 20, sigmoid_low = 5, resistance = -1,
             threshold_resistance = 1e9, wait_for_complete = True):
        """
        !!!!!THIS FUNCTION WILL BE DEPRECATED, USE eburn INSTEAD!!!!!


        parameters for communicating with the adwin
        'Par_40 = Busy'
        'Par_31 = input channel'
        'Par_32 = output channel'
        'Par_33 = n (number of cycle)'
        'Par_34 = breakpoint voltage'
        'Par_35 = hold counter at 10 V
        'Par_36 = processdelay
        'Par_37 = trigger type

        'Par_38 = flag ohmic resistance'
        'Par_39 = amount of datapoints'

        'FPar_10 = Ramp Up Step
        'FPar_11 = Ramp Down Step
        'FPar_12 = sigmoid center
        'FPar_13 = sigmoid steepness
        'FPar_14 = approximate left side
        'FPar_15 = approximate right side
        'FPar_16 = burn gain (in powers)
        'FPar_17 = resistance
        'FPar_18 = threshold resistance
        """
        #print('Warning: the function burn will be deprecated and is no longer supported, use eburn instead.')
        self.set_gain(self.burn_gain)
        # change the sigmoidal functions
        sigmoid_high *= 10 ** (self.burn_gain-4)
        sigmoid_low *= 10 ** (self.burn_gain - 4)
        # set the required parameters for the script
        self._adwin.set('par31', self._input_channel)
        self._adwin.set('par32', self._output_channel)
        self._adwin.set('par33', cycle_num)
        self._adwin.set('par34', self._voltage_to_digit(max_voltage))
        self._adwin.set('par35', hold_at_10/(process_delay/PROCESS_CLOCK))
        self._adwin.set('par36', process_delay)  # process delay
        self._adwin.set('fpar10', ramp_up)
        self._adwin.set('fpar11', ramp_down)
        self._adwin.set('fpar12', sigmoid_center)
        self._adwin.set('fpar13', sigmoid_steepness)
        self._adwin.set('fpar14', sigmoid_high)
        self._adwin.set('fpar15', sigmoid_low)
        self._adwin.set('fpar16', 10 ** self.burn_gain)
        self._adwin.set('fpar17', resistance)
        self._adwin.set('fpar18', threshold_resistance)
        self._busy_par = 'par40'
        self._adwin.start_process(5)
        if wait_for_complete:
            while self._adwin.get(self._busy_par): pass  # test the busy parameter until adwin is finished one cycle
            count = self._adwin.get('par39')  # get the amount of datapoints
            v = np.array(self._adwin.get('data1')[:count]) * (20.0 / 65535) - 10.0  # get voltage digit and transform into real units
            i = np.array(self._adwin.get('data2')[:count]) * (20.0 / 65535) - 10.0  # get current digit transform into real units
            flag = self._adwin.get('par37')  # get the burn flags
            if not v.size and not i.size:
                flag |= ADWIN_FLAG_NO_DATA
            if np.max(np.absolute(i)) < _UNDERLOAD_THRESHOLD:
                flag |= ADWIN_FLAG_UNDERLOAD
            elif np.max(np.absolute(i)) > _OVERLOAD_THRESHOLD:
                flag |= ADWIN_FLAG_OVERLOAD
            return [v, i*(10**(-self.burn_gain)), flag]
        else:
            return [[],[],ADWIN_FLAG_DATA_INCOMPLETE | ADWIN_FLAG_NO_DATA]

    def current_time_trace(self, v, electrode = 'source', data_frequency = 10, num_datapoints = 100,
                           num_average = 1, wait_for_complete = True):
        self.write(v,electrode=electrode)
        self.read()  # this handles autogain at the set voltage
        self._adwin.set('par51', self._output_channel)
        self._adwin.set('par52', self._input_channel)
        self._adwin.set('par53', self._voltage_to_digit(v))
        processdelay = int(PROCESS_CLOCK / (data_frequency * num_average))
        if processdelay < PROCESSDELAY_MINIMUM:
            print("Warning: attempting to measure too fast, decrease data_frequency or num_average.")
        self._adwin.set('par54', processdelay)
        self._adwin.set('par55', num_average)
        self._adwin.set('par56', num_datapoints)

        self._busy_par = 'par60'
        self._adwin.start_process(6)
        if wait_for_complete:
            while self._adwin.get(self._busy_par): pass  # test the busy parameter until adwin is finished
            t = np.array(self._adwin.get('data1')[:num_datapoints]) * (processdelay/PROCESS_CLOCK)  # get voltage digit and transform into real units
            i = np.array(self._adwin.get('data2')[:num_datapoints]) * (20.0 / 65535) - 10.0  # get current digit transform into real units
            flag = 0
            if not t.size and not i.size:
                flag |= ADWIN_FLAG_NO_DATA
            if np.max(np.absolute(i)) < _UNDERLOAD_THRESHOLD:
                flag |= ADWIN_FLAG_UNDERLOAD
            elif np.max(np.absolute(i)) > _OVERLOAD_THRESHOLD:
                flag |= ADWIN_FLAG_OVERLOAD
            return [t, i*(10**(-self.iv_gain)), flag]
        else:
            return [[],[],ADWIN_FLAG_DATA_INCOMPLETE | ADWIN_FLAG_NO_DATA]
