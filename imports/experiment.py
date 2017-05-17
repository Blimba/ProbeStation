import importlib
import time
import os
import shutil

class Experiment(object):
    _info_file = ''
    _t0=0
    def __init__(self, qt, script_file, name, devices):
        self._qt = qt
        self._script = script_file
        self._exp = importlib.import_module(script_file)
        self._instr = self._exp.init(qt)
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

    def run(self, device):
        if device in self._devices:
            print("Running experiment %s on device %s" % (self._script, device))
            output = [device, str(time.time() - Experiment._t0), self._script]
            o = self._exp.start(self._qt,self._instr,self._name,device)
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
        try: self._exp.end(self._qt, self._instr, self._name)
        except: pass
