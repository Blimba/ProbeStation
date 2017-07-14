import qt
import numpy as np
class HP(object):
    def __init__(self, source=1, gate=2, drain=3, screen_refresh=False):
        self.instr = qt.instruments.create('hp4156a','HP_4156A_BL',address='GPIB::17')
        self._source = source
        self._gate = gate
        self._drain = drain
        self._screen_refresh = 1 if screen_refresh else 0

    def write(self, v, electrode='source'):
        self.instr.set('screen_refresh', self._screen_refresh)
        if electrode=='gate':
            self.instr.set('smu_source%d' % self._gate, v)
        else:
            self.instr.set('smu_source%d' % self._source, v)
        self.instr.set('screen_refresh', 1)

    def sweep_triangle(self, v_min=-0.4, v_max=0.4, v_step=0.01, electrode='source'):
        self.instr.set('screen_refresh', self._screen_refresh)
        sw = self._source
        if electrode == 'gate':
            sw = self._gate
        if v_min < 0 and v_max > 0:
            self.instr.sweep(channel=sw,
                        start=0,
                        stop=v_max,
                        step=v_step,
                        channel_list=[1, 2, 3],
                        retrace=True,
                        spacing='LIN')
            self.instr.set('smu_source%d' % self._drain, 0.0)
            self.instr.measure()
            self.instr.sweep(channel=sw,
                        start=0,
                        stop=v_min,
                        step=v_step,
                        channel_list=[1, 2, 3],
                        retrace=True,
                        spacing='LIN')
            self.instr.measure(append=True)
            v = np.array(self.instr.get('smu_v%d' % sw))
            i = -np.array(self.instr.get('smu_i%d' % self._drain))
        elif v_min == 0 or v_max == 0:
            if v_min == v_max:
                self.instr.set('screen_refresh', 1)
                return [0,0]
            stop = v_min
            if not stop:
                stop = v_max
            self.instr.sweep(channel=sw,
                             start=0,
                             stop=stop,
                             step=v_step,
                             channel_list=[1, 2, 3],
                             retrace=True,
                             spacing='LIN')
            self.instr.set('smu_source%d' % self._drain, 0.0)
            self.instr.measure()
            v = np.array(self.instr.get('smu_v%d' % sw))
            i = -np.array(self.instr.get('smu_i%d' % self._drain))
        else:
            self.instr.set('screen_refresh', 1)
            return [0,0]
        self.instr.set('screen_refresh', 1)
        return [v, i]

    def zero(self):
        self.instr.set('smu_func1', 'CONS')
        self.instr.set('smu_func2', 'CONS')
        self.instr.set('smu_func3', 'CONS')
        self.instr.set('smu_source1', 0.0)
        self.instr.set('smu_source2', 0.0)
        self.instr.set('smu_source3', 0.0)