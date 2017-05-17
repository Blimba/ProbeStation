import re
class Cascade(object):

    def __init__(self,qt):
        self.qt=qt
        print('Initialising Cascade...')
        self.instr = qt.instruments.create('cascade','Cascade_Summit_12000')
        print('Cascade initialised.')
        self._position=[0,0]

    def move_abs(self,pos): #move the cascade to an absolute position
        print("moving the head: "+str(pos[0]-self._position[0])+","+str(pos[1]-self._position[1]))
        self.instr.set('position',[pos[0]-self._position[0],-(pos[1]-self._position[1]),0],rel=True)
        self.position=pos
        self.qt.msleep(2)

    def state(self):
        if self.instr.get('contact'):
            return 'down'
        else:
            return 'up'

    def down(self):
        self.instr.set('contact',1)
        print("probes down")
    def up(self):
        self.instr.set('contact',0)
        print("probes up")

    def store_position_file(self,filename):
        try:
            f = open(filename,'r')
            posstr = f.read()
            m = re.match(' *(\d+)( |x|,)(\d+) *',posstr)
            if m:
                g = m.groups()
                self._position = (int(g[0]), int(g[2]))
            f.close()
        except:
            try:
                f = open(filename, 'w')
                f.close()
            except:
                print("Warning, couldn't write to position storing file!")
                return False
            self._pos_file = filename
            return False
        self._pos_file = filename
        return True

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self,pos):
        self._position = pos
        if self._pos_file:  # write to position storer
            try:
                with open(self._pos_file, 'w') as f:
                    f.write(str(pos[0])+','+str(pos[1]))
            except:
                print("Warning: could not save cascade position to file.")
                pass

