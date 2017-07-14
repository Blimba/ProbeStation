import qt
class data(object):
    def __init__(self, name, coordinates, values, dev=''):
        self._name = name
        self._dev = dev
        self._plots = {}
        if dev:
            self._data = qt.Data(name='%s_%s' % (name,dev))
        else:
            self._data = qt.Data(name=name)
        self._data.create_file(settings_file=False)  # we don't want heavy 1 MB files to be created alongside of the data file
        self._coords = []
        self._vals = []
        if type(coordinates) is list or type(coordinates) is tuple:
            for coord in coordinates:
                self._coords.append(coord)
                self._data.add_coordinate(coord)
        else:
            self._coords.append(str(coordinates))
            self._data.add_coordinate(str(coordinates))
        if type(values) is list or type(values) is tuple:
            for val in values:
                self._vals.append(val)
                self._data.add_value(val)
        else:
            self._vals.append(str(values))
            self._data.add_value(str(values))

    def fill(self, *args, **kwargs):
        if args:
            if len(args) != len(self._coords) + len(self._vals):
                print('Error (data.fill): data does not match dimensionality.')
                return
        else:
            args = []
            for key in self._coords:
                if not key in kwargs:
                    print('Error (data.fill): Key error in data. ')
                    return
                args.append(kwargs[key])
            for key in self._vals:
                if not key in kwargs:
                    print('Error (data.fill): Key error in data. ')
                    return
                args.append(kwargs[key])
        self._data.add_data_point(*args)

    def add_data_point(self, *args, **kwargs):
        self.fill(*args, **kwargs)

    def new_block(self):
        self._data.new_block()

    def plot3d(self, coorddims=(0,1), valdim=2, traceofs=0, **kwargs):
        name = kwargs.get('name',self._name)
        if name in self._plots:
            self._plots[name].update()
        else:
            self._plots[name]=qt.Plot3D(name=name, coorddims=coorddims, valdim=valdim, traceofs=traceofs, **kwargs)

    def plot2d(self, coorddim=0, valdim=0, traceofs=0, **kwargs):
        if valdim == 0:
            valdim = len(self._coords)
        name = kwargs.get('name', self._name)
        if name in self._plots:
            self._plots[name].update()
        else:
            self._plots[name]=qt.Plot2D(name=name, coorddim=coorddim, valdim=valdim, traceofs=traceofs, **kwargs)

    def plot(self, **kwargs):
        if len(self._coords) > 1:
            self.plot3d(**kwargs)
        else:
            self.plot2d(**kwargs)

    def close(self):
        self._data.close_file()

    def close_file(self):
        self.close()