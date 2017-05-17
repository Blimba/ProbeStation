from scipy import stats

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

def create_data_file(qt, name, coordinates, values):
    dat = qt.Data(name=name)
    dat.create_file(settings_file=False)  # we don't want heavy 1 MB files to be created alongside of the data file
    if type(coordinates) is list or type(coordinates) is tuple:
        for coord in coordinates:
            dat.add_coordinate(coord)
    else:
        dat.add_coordinate(str(coordinates))
    if type(values) is list or type(values) is tuple:
        for val in values:
            dat.add_value(val)
    else:
        dat.add_value(str(values))

    return dat

