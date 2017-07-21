'''

This part of the script defines the chip architecture and the devices on the chip. You can easily load different chips
from template files or directly define it from the script. Then, you can load a part of the chip to list devices on.

For example, you can load the T2.ini chip template, which has columns a to w, and row 1 to 38, of which row 38 is
shorted. Then, you can load devices on column a only, to create a run list for the devices on column a only.

User callable functions:

------------------------------------------------------------------------------------------------------------------------

__init__(name, **kwargs):

initialises the chip class. Usage:
c=Chip(experiment_name)

You may pass a template here too (see below for load_template) like so:
c=Chip(experiment_name, template='2T.ini')

------------------------------------------------------------------------------------------------------------------------

c.define_devices(device_square, position=(0,0), pitch=(0,0), hide_from_range=False)

define a chip architecture. For the T2 chip, we would run this function twice:
c.define_devices('a1-w37', (0,0), (400, 200), False)
c.define_devices('a38-w38', (0, 7400), (400, 200), True)

First, the 'normal' area of the chip is defined. The devices a1 to w37 define a square including all devices in between
the column and row numbers (i.e., a1-b2 would include a1, a2, b1 and b2). The initial position of device a1 is (0,0),
i.e., 0 for x and 0 for y. The spacing between devices (pitch) is 400 for x and 200 for y. The devices are not hidden
from the range (see c.load_devices below).

Then, we include the shorted devices on row 38. The devices a38-w38 include all columns for row 38. The position of the
first device (a38) is at 0 for x and 7400 for y. The pitch is the same as before. These devices are hidden from the
range (see c.load_devices below).

------------------------------------------------------------------------------------------------------------------------

c.load_template(filename, ignore_hidden=True)

Loads a chip template from a file. Chip template files should have lines corresponding to:
device_range, (position_x, position_y), (pitch_x, pitch_y)

The word 'hidden' may be added to the start of the line to indicate these devices should be hidden from the range (see
c.load_devices below).

Other lines in the file will be ignored by the script (to be sure, add # as a comment to the start of the line).

------------------------------------------------------------------------------------------------------------------------

c.load_devices(device_range)

This function creates the 'run list' of the devices (see c.devices below). This means that you can only load a part of
the devices on the chip to run. The device_range here works differently than the square method described above. Instead,
it will run column by column.

For example, on the T2 chip:
c.load_devices('a') # would list a1-a37
Note: a38 is NOT added to the list because it is hidden from the device range (see above). You could run it by
specifically calling c.load_devices('a1-a38')

Other examples:
c.load_devices('a3') # would list only device a3
c.load_devices('a3-6') # would list devices a3, a4, a5 and a6
c.load_devices('a36-b2') # would list devices a36, a37, b1 and b2
c.load_devices('a-c') # would list all the devices on columns a, b and c (except row 38, because it is hidden)
c.load_devices('a38') # would list only device a38 (even though it is hidden, you can still access it)
c.load_devices('*') # lists all the devices on the chip

Ranges may be subsequently added by comma separation:
c.load_devices('a3,a3-6') # this would list a3 twice, followed by a4, a5 and a6.

------------------------------------------------------------------------------------------------------------------------

c.load_from_file(filename)

Loads the device range from a file. See c.load_devices above for details.

------------------------------------------------------------------------------------------------------------------------

c.start_at_device(dev,run_skipped_devices=False)

Sorts the device list (see c.devices below) to start at a certain device in the list. If run_skipped_devices is False,
the list will exclude the devices that were on the list prior to the device specified. For example, the following code
would generate a list containing devices a35, a36 and a37, ignoring the other devices:
c.load_devices('a')
c.start_at_device('a35',False)

Otherwise, the following code would be equivalent to c.load_devices('a35-37,a1-34'):
c.load_devices('a')
c.start_at_device('a35',True)

------------------------------------------------------------------------------------------------------------------------

c.add_experiment(script_file,devices='*'):

defines an experiment for a device square (so, like in c.define_devices, not a range like in c.load_devices).
For example:
c.add_experiment('test','a1-b2')
would add the experiment 'test' to the experiment list for devices a1, a2, b1 and b2 only. For the other devices, no
experiment (or another experiment) are run.
You may add as many experiments as you see fit, and multiple experiments may be added to the same device; in such a
case, the experiments will be run in order that they were added.

The experiment 'test' will need an addition python file in the main script directory, called test.py. This file will
need specific functions, as explained in the documentation of main.py.

------------------------------------------------------------------------------------------------------------------------

c.get_device_position(dev)

Returns the device position as a tuple of shape (position_x, position_y). Obviously, this only works for devices that
are defined on the chip. If the device is not on the chip, the position (-1, -1) is returned.

------------------------------------------------------------------------------------------------------------------------

c.get_device_from_position(position)

Returns the device at a certain position (input a tuple of shape (position_x, position_y). If the position does not
contain a device, an empty string is returned.

------------------------------------------------------------------------------------------------------------------------

c.devices # property

This is the list of devices that should be run on the chip, and is populated by c.load_devices or by c.load_from_file.

------------------------------------------------------------------------------------------------------------------------

c.experiments

This is the list of experiments that are populated by c.add_experiment. As seen in main.py, the correct way of running
experiments on the loaded devices is:

for device in c.devices:
    # move cascade here
    for experiment in c.experiments:
        experiment.run(device)

Note: the cascade movement is NOT included in this code. The experiment.run code checks if the experiment should be run
for the device, and otherwise nothing is returned.

'''


import re
try: from imports.experiment import *
except:
    class Experiment:
        def __init__(self,*args,**kwargs):
            pass
        @staticmethod
        def restart():
            pass

class Chip:
    def _w2d(self,w):
        '''
        transforms column letter to column number
        :param w:
        :return column number (int):
        '''
        w = w.lower()
        base = ord('z')-ord('a')+1
        d = 0
        for index, ch in enumerate(reversed(w)):
            if index > 0:
                d += base ** index * (ord(ch) - ord('a') + 1)
            else:
                d += base**index * (ord(ch)-ord('a'))
        return d
    def _d2w(self,d):
        '''
        transform column number to column letter
        :param d:
        :return column letter (string):
        '''
        base = ord('z') - ord('a') + 1
        w=''
        d+=1
        while d > 0:
            mod = (d - 1) % base
            w = str(chr(ord('a')+int(mod)))+w
            d = (d-mod)//base
        return w

    def __iter__(self):
        return self._run_dev_list.__iter__()

    def __contains__(self, item):
        return self._run_dev_list.__contains__(item)

    def __init__(self, name, **kwargs):
        self._dev_list = {}
        self._test_dev_list = {}
        self._run_dev_list = []
        self._cols = []
        self._experiments = []
        self._name = name
        Experiment.restart()
        if 'template' in kwargs:
            self.load_template(kwargs['template'],kwargs.get('ignore_hidden',True))


    def define_devices(self, device_square, position=(0,0), pitch=(0,0), hide_from_range=False):
        '''
        defines the device architecture on the chip.

        the device ranges are interpreted as a square.
        For example:
        a1-b2 will include devices a1, a2, b1 and b2.
        a1 is positioned at the position supplied
        a2 is offset by the y pitch
        b1 is offset by the x pitch
        b2 is offset by both the x and y pitch.

        :param device_range:
        :param position:
        :param pitch:
        :return nothing:
        '''
        m=re.findall(' *([a-zA-Z]+)(\d+)-([a-zA-Z]+)(\d+)', device_square)
        for index, r in enumerate(m):
            r = list(r)
            # exclude the last "match"
##            if index == len(m)-1:
##                continue
            if not r[1]:
                r[1] = r[3]
            if not r[3]:
                r[3] = r[1]
            if not r[0]:
                r[0] = r[2]
            if not r[2]:
                r[2] = r[0]
            if r[1] > r[3]:
                t = r[1]
                r[1] = r[3]
                r[3] = t
            wd1 = self._w2d(r[0])
            wd2 = self._w2d(r[2])
            if wd2 < wd1:
                t = wd1
                wd1=wd2
                wd2=t
            if (not r[0] or not r[1]):
                r = m[index]
                print('Warning: illegal device range supplied: %s%s-%s%s' % (r[0],r[1],r[2],r[3]))
                continue
            d_range = range(int(r[1]),int(r[3])+1)
            w_range = range(wd1,wd2+1)
            for w_index, dw in enumerate(w_range):
                if not self._d2w(dw) in self._cols and not hide_from_range:
                    self._cols.append(self._d2w(dw))
                for d_index, d in enumerate(d_range):
                    pos = (position[0] + pitch[0] * w_index, position[1]+pitch[1]*d_index)
                    try:
                        if not self._d2w(dw)+str(d) in self._dev_list and not hide_from_range:
                            self._dev_list[self._d2w(dw)].append(d)
                    except KeyError:
                        self._dev_list[self._d2w(dw)]=[]
                        if not hide_from_range:
                            self._dev_list[self._d2w(dw)].append(d)
                    self._dev_list[self._d2w(dw)+str(d)] = pos
                    
    def _dev_square_to_list(self, device_square):
        lst = []
        if '*' in device_square:
            device_square = '%s%d-%s%d' % (self._cols[0], self._dev_list[self._cols[0]][0], self._cols[-1], self._dev_list[self._cols[-1]][-1])
        m = re.findall(' *([a-zA-Z]+)(\d+)-([a-zA-Z]+)(\d+)', device_square)
        for index, r in enumerate(m):
            r = list(r)
            # exclude the last "match"
            if not r[1]:
                r[1] = r[3]
            if not r[3]:
                r[3] = r[1]
            if not r[0]:
                r[0] = r[2]
            if not r[2]:
                r[2] = r[0]
            if r[1] > r[3]:
                t = r[1]
                r[1] = r[3]
                r[3] = t
            wd1 = self._w2d(r[0])
            wd2 = self._w2d(r[2])
            if wd2 < wd1:
                t = wd1
                wd1 = wd2
                wd2 = t
            if (not r[0] or not r[1]):
                r = m[index]
                print('Warning: illegal device range supplied: %s%s-%s%s' % (r[0], r[1], r[2], r[3]))
                continue
            d_range = range(int(r[1]), int(r[3]) + 1)
            w_range = range(wd1, wd2 + 1)
            lst=[]
            for w_index, dw in enumerate(w_range):
                for d_index, d in enumerate(d_range):
                    dev = self._d2w(dw)+str(d)
                    if dev in self._dev_list:
                        lst.append(dev)
        return lst

    def _dev_range_to_list(self, device_range):
        lst = []
        if '*' in device_range:
            device_range = device_range.replace('*','%s-%s' % (self._cols[0], self._cols[-1]))
        m = re.findall(' *,? *([a-zA-Z]+)(\d*)-?([a-zA-Z]*)(\d*)', device_range)
        for index, r in enumerate(m):
            r = list(r)
            if not r[0]: continue  # first column should be set
            if not r[1]:
                dorow = True
                r[1] = 1  # if first row isn't set, assume 1
            else:
                dorow = False
            if not r[2]:
                r[2] = r[0]  # if the second column isn't set, it should be the same as the first
            if not r[3] and not dorow and r[2] == r[0]:
                r[3] = r[1]  # if it is a single device, set r3 = r1
            elif not r[3]:
                r[3] = self._dev_list[r[2]][-1]  # if it is multiple columns, go til the end
            # make w range
            try:
                cols = self._cols[self._cols.index(r[0]):self._cols.index(r[2]) + 1]
            except:
                continue
            for c_index, col in enumerate(cols):
                d1 = int(r[1])
                if c_index > 0:
                    d1 = 1
                d2 = int(self._dev_list[col][-1])
                if c_index == len(cols) - 1:
                    d2 = int(r[3])
                try:
                    _ = self._dev_list[col][d1 - 1]
                    _ = self._dev_list[col][d2 - 1]
                    d_range = self._dev_list[col][d1 - 1:d2]
                    if len(d_range) < 2:
                        d_range=range(d_range,d_range+1)
                except:
                    d_range = range(d1, d2 + 1)
                for d_index, d in enumerate(d_range):
                    # if not d in self._dev_list
                    dev = col + str(d)
                    if dev in self._dev_list:
                        lst.append(dev)
        return lst

    def load_template(self, filename, ignore_hidden=True):
        '''

        load chip architecture from a file.
        The file should have lines using the following format:

        device range, (position x, position y), (pitch x, pitch y)

        The word 'hidden' can be added in front to exclude the device range for looping over (for example, for testing)
        for example, for the T2 chip, the template file is:

        a1-w37, (0, 0), (400, 200)
        hidden a38-w38, (7400, 0), (400, 200)

        Row 38 is ignored when a device-range a-b is loaded.

        any other lines are considered comments and are ignored.

        :param filename with template:
        :return True if successful, False if unsuccessful:
        '''
        try:
            f = open('templates/%s' % filename, "r")
        except:
            f = open(filename, "r")
        for line in f:
            m = re.match(
                ' *(hidden|test|exclude)? *([a-zA-Z0-9\-]+) *, *\( *(-?\d*\.?\d+) *, *(-?\d*\.?\d+) *\) *, *\( *(-?\d*\.?\d+) *, *(-?\d*\.?\d+) *\) *',
                line)
            if m:
                g = list(m.groups())
                if not ignore_hidden:  # just add all devices, do not ignore hidden
                    g[0] = False
                self.define_devices(g[1], position=(float(g[2]), float(g[3])), pitch=(float(g[4]), float(g[5])),
                                    hide_from_range=bool(g[0]))
        f.close()
        return True

    def limit_range(self, device_square):
        lst = self._dev_square_to_list(device_square)
        it = [dev for dev in self._dev_list]
        for dev in it:
            m = re.match(' *([a-zA-Z]+)([0-9]+) *', dev)
            if m:
                if not dev in lst:
                    del self._dev_list[dev]
                    try:
                        self._dev_list[m.group(1)].remove(int(m.group(2)))
                        if not len(self._dev_list[m.group(1)]):
                            del self._dev_list[m.group(1)]
                            self._cols.remove(m.group(1))
                    except:
                        pass

    def load_devices(self, device_range):
        '''
        generates the device list that should be run by the program.
        Use comma separation for ranges.
        For example:
        a-c does all devices in columns a, b and c
        a3-5 does devices a3, a4 and a5
        a3-b5 does all devices in a starting from a3, and continues to do all devices in b until (including) b5

        :param device_range:
        :return nothing:
        '''
        self._run_dev_list = self._dev_range_to_list(device_range)

    def load_from_file(self,filename):
        '''

        loads a device list from a file. Use comma separation for ranges.
        For example:
        a-c does all devices in columns a, b and c
        a3-5 does devices a3, a4 and a5
        a3-b5 does all devices in a starting from a3, and continues to do all devices in b until (including) b5

        :param filename:
        :return True if successful, False if unsuccessful:
        '''
        try:
            f = open(filename, "r")
            self.load_devices(f.read())
            f.close()
        except:
            return False
        return True


    def start_at_device(self,dev,run_skipped_devices=False):
        # try to find the index of the current device in the list, otherwise, start from the beginning
        index = 0
        try:
            index = self._run_dev_list.index(dev)
        except ValueError:
            try:
                dev = self._run_dev_list[0]
            except:
                raise SystemError('No devices loaded, exiting...')
        if run_skipped_devices:
            self._run_dev_list = self._run_dev_list[index:] + self._run_dev_list[:index]
        else:
            self._run_dev_list = self._run_dev_list[index:]
        return dev

    def add_experiment(self,script_file,devices='*'):
        '''
        add an experiment to the experiment list. The execute_experiment function will run over experiments and run them
        :param script_file:
        :param devices:
        :return:
        '''
        device_list = self._dev_square_to_list(devices)
        print(device_list)
        exp = Experiment(script_file, name=self._name, devices=device_list)
        self._experiments.append(exp)
        return exp

    def get_device_position(self,dev):   #gets the absolute position of a device from the origin point (0,0)
        m = re.match(' *([a-z]+[0-9]+) *',dev)
        if m:
            d = m.group(1)
            if not d in self._dev_list:
                return (-1,-1)
            return (self._dev_list[dev][0], self._dev_list[dev][1])
        return (-1,-1)

    def get_device_from_position(self,position):
        for dev in self._dev_list:
            if len(self._dev_list[dev]) > 1:
                if self._dev_list[dev][0] == position[0] and self._dev_list[dev][1] == position[1]:
                    return dev
        return ''

    @property
    def experiments(self):
        return self._experiments

    @property
    def devices(self):
        '''
        :return the device list that should be run by the program:
        '''
        return self._run_dev_list

    @devices.setter
    def devices(self,devices):
        self._run_dev_list = devices
