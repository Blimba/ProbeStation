import importlib
import time
import os
import shutil
import qt

class Experiment(object):
    _info_file = ''
    _t0=0
    @staticmethod
    def restart():
        Experiment._info_file=''
        Experiment._t0 = 0

    def __init__(self, script_file, name, devices):
        self.script = script_file
        print 'Importing %s/%s' % (os.getcwd(), script_file)
        self._exp = importlib.import_module(script_file)
        reload(self._exp) # in case the code was changed
        self._instr = self._exp.init()
        self._name = name
        self._devices = devices
        # generate the experiment info file
        if not Experiment._info_file:
            d = qt.Data(name='%s_info' % (name))
            d.create_file(settings_file=False)
            d.close_file()
            Experiment._info_file = d.get_filepath()
            Experiment._t0 = time.time()
        # save the current python script as a copy for future lookup
        shutil.copy(script_file+'.py', os.path.dirname(Experiment._info_file))

    def __contains__(self, item):
        return item in self._devices

    def get_switch_settings(self):
        try:
            settings = self._exp.get_switch_settings()
        except:
            settings = None
        return settings



    def run(self, device, **kwargs):
        if device in self._devices:
            print("Running experiment %s on device %s" % (self.script, device))
            output = [device, str(time.time() - Experiment._t0), self.script]
            o = self._exp.start(self._instr,self._name, device, **kwargs)
            if type(o) is list or type(o) is tuple:
                for j in range(len(o)):
                    output.append(str(o[j]))
            else:
                output.append(str(o))
            try:
                with open(self._info_file, "a") as f:
                    f.write('\t'.join(output) + '\n')
            except:
                print("Warning: couldn't save experimental info to file.")
            return output
        return []

    def end(self):
        try: self._exp.end(qt, self._instr, self._name)
        except: pass
