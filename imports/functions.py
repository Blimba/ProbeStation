from scipy import stats
import qt
import thread

def add_metric_prefix(d):
    """
    :param d:
    :return string:

      the function takes a floating point number, and outputs the value as a number between 1-999 with order of
      magnitude added.
    """
    unit_list = ['f', 'p', 'n', 'u', 'm', '', 'k', 'M', 'G', 'T']
    unit = 5
    if d == 0:
        return "0"
    while abs(d) >= 1000 and unit < len(unit_list)-1:
        d = d / 1000
        unit += 1
    while (abs(d) < 1 and unit > 0):
        d = d * 1000
        unit -= 1
    return "%.2f %s" % (d, unit_list[unit])


def linear_fit_resistance(Vdata, Idata):
    """
    :param Vdata:
    :param Idata:
    :return the resistance of a linear fit across the data:
    """
    slope, intercept, r_value, p_value, std_err = stats.linregress(Vdata, Idata)
    return 1 / slope  # return resistance

def sleep(seconds):
    qt.msleep(seconds)

class Input:
    def _wait(self, lst):
        lst.append(raw_input())
    def __init__(self):
        self.lst = []
        self.waiting = True
        thread.start_new_thread(self._wait, (self.lst,))
    def check_input(self):
        if self.lst:
            del self.lst[0]
            self.waiting = False
            return True
        else:
            return False

_input = Input()
def check_user_input(str=''):
    global _input
    if not _input.waiting:
        _input = Input()
    if _input.check_input():
        msg = ''
        while msg != 'exit' and msg != 'continue':
            if str:
                msg = raw_input("Program flow paused. What would you like to do (exit/continue/%s)? " % str)
                if msg == str:
                    break
            else:
                msg = raw_input("Program flow paused. What would you like to do (exit/continue)? ")
        if msg == 'exit':
            print('Exiting program...')
            raise SystemExit()
        return msg
    else:
        return ''