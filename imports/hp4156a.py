import qt
import numpy as np
class HP(object):
    instr = 0
    def __init__(self, source=1, drain=2, gate=3, screen_refresh=False):
        if not HP.instr:
            HP.instr = qt.instruments.create('hp4156a','HP_4156A_BL',address='GPIB::17')
        self._source = source
        self._gate = gate
        self._drain = drain
        self._screen_refresh = 1 if screen_refresh else 0

    def write(self, v, electrode='source'):
        HP.instr.set('screen_refresh', self._screen_refresh)
        if electrode=='gate':
            HP.instr.set('smu_source%d' % self._gate, v)
        else:
            HP.instr.set('smu_source%d' % self._source, v)
        HP.instr.set('screen_refresh', 1)

    def sweep_triangle(self, v_min=-0.4, v_max=0.4, v_step=0.01, electrode='source', source=0, gate=0):
        HP.instr.set('screen_refresh', self._screen_refresh)
        sw = self._source
        if electrode == 'gate':
            sw = self._gate
        if v_min < 0 and v_max > 0:
            HP.instr.sweep(channel=sw,
                        start=0,
                        stop=v_max,
                        step=v_step,
                        channel_list=[1, 2, 3],
                        retrace=True,
                        spacing='LIN')
            HP.instr.set('smu_source%d' % self._drain, 0.0)
            if electrode=='gate':
                HP.instr.set('smu_source%d' % self._source, source)
            else:
                HP.instr.set('smu_source%d' % self._gate, gate)
            HP.instr.measure()
            HP.instr.sweep(channel=sw,
                        start=0,
                        stop=v_min,
                        step=v_step,
                        channel_list=[1, 2, 3],
                        retrace=True,
                        spacing='LIN')
            HP.instr.measure(append=True)
            v = np.array(HP.instr.get('smu_v%d' % sw))
            i = -np.array(HP.instr.get('smu_i%d' % self._drain))
        elif v_min == 0 or v_max == 0:
            if v_min == v_max:
                HP.instr.set('screen_refresh', 1)
                return [0,0]
            stop = v_min
            if not stop:
                stop = v_max
            HP.instr.sweep(channel=sw,
                             start=0,
                             stop=stop,
                             step=v_step,
                             channel_list=[1, 2, 3],
                             retrace=True,
                             spacing='LIN')
            HP.instr.set('smu_source%d' % self._drain, 0.0)
            if electrode=='gate':
                HP.instr.set('smu_source%d' % self._source, source)
            else:
                HP.instr.set('smu_source%d' % self._gate, gate)
            HP.instr.measure()
            v = np.array(HP.instr.get('smu_v%d' % sw))
            i = -np.array(HP.instr.get('smu_i%d' % self._drain))
        else:
            HP.instr.set('screen_refresh', 1)
            return [0,0]
        HP.instr.set('screen_refresh', 1)
        return [v, i]

    def zero(self):
        HP.instr.set('smu_func1', 'CONS')
        HP.instr.set('smu_func2', 'CONS')
        HP.instr.set('smu_func3', 'CONS')
        HP.instr.set('smu_source1', 0.0)
        HP.instr.set('smu_source2', 0.0)
        HP.instr.set('smu_source3', 0.0)
