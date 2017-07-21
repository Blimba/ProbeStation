import qt

class SignalSwitch(object):
    _instr = 0
    def __init__(self):
        self.settings = {}
        self.curr_settings = [0,0,0]
        if not SignalSwitch._instr:
            try:
                SignalSwitch._instr = qt.instruments.create('Arduino','Arduino',address='COM11')
            except:
                print('Warning: signal switcher could not be initialised.')
                SignalSwitch._instr = 'NA'

    def route(self, channel, destination):
        if destination == 'HP' and SignalSwitch._instr == 'NA':
            print('Warning: signal switcher could not switch to HP.')
        else:
            if self.curr_settings[channel-1] != destination:
                print('Routing channel %d: %s' % (channel, destination))
                SignalSwitch._instr.set('pin%d' % channel, destination)
                self.curr_settings[channel-1] = destination

    def route_settings(self,settings):
        for i in range(3):
            if type(settings) is tuple or type(settings) is list:
                self.route(i+1,settings[i])
            else:
                self.route(i+1,settings)

    def add_settings(self,script,settings):
        self.settings[script] = settings

    def load_settings(self,script):
        try: settings = self.settings[script]
        except:
            if script[:2].lower() == 'hp':
                settings = 'HP'
            else:
                settings = 'ADWIN'
        return settings
