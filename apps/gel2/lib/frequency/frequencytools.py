from math import log10
from math import floor as mathfloor

from ..utils.regexcompiler import ReMatcher

parsed_labels = dict()
midpoints = dict()
moving_average_windowsize = [(1900, 6), (1950, 4), (2020, 2)]


class FrequencyTools(object):

    def __init__(self, data):
        self.parse_data(data)

    def parse_data(self, data):
        self.d = dict()
        for p, v in data.items():
            if isinstance(p, int) and p > 1700 and p < 2050:
                dp = DataPoint(year=p, frequency=v)
                self.d[dp.year] = dp
            elif isinstance(p, basestring):
                m = ReMatcher(p)
                if m.search(r"^f([0-9]{4})$"):
                    dp = DataPoint(year=int(m.group(1)), frequency=v)
                    self.d[dp.year] = dp

    def data(self):
        return self.d

    def data_list(self):
        return [(y, self.data()[y].frequency)
                for y in sorted(self.data().keys())]

    def last_year(self):
        return self.data_list()[-1][0]

    def frequency(self, year=2000):
        if year in self.data():
            return self.data()[year].frequency
        else:
            return self.data()[self.last_year()].frequency

    def band(self, year=2000):
        if year in self.data():
            return self.data()[year].band()
        else:
            return self.data()[self.last_year()].band()

    def log(self, year=2000):
        if year in self.data():
            return self.data()[year].log_frequency()
        else:
            return self.data()[self.last_year()].log_frequency()

    def delta(self, year1, year2):
        """Change over time (as a ratio)
        """
        if self.frequency(year=year1) < 0.00000001:
            return None
        else:
            return self.frequency(year=year2) / self.frequency(year=year1)

    def interpolated(self):
        try:
            return self.interpol
        except AttributeError:
            self.interpol = []
            for yr in sorted(self.data().keys()):
                self.interpol.append(self.data()[yr])
            return self.interpol

    def moving_average(self):
        try:
            return self.mov_av
        except AttributeError:
            averaged_y = []
            start_point_passed = False
            for i, dp in enumerate(self.interpolated()):
                windowsize = None
                for block in moving_average_windowsize:
                    if dp.year < block[0]:
                        windowsize = block[1]
                        break
                span = int(windowsize / 2)
                first = max(i - span, 0)
                last = min(i + span + 1, len(self.interpolated()))
                window = self.interpolated()[first:last]
                if dp.frequency > 0:
                    start_point_passed = True
                if not window:
                    av = 0
                elif dp.frequency == 0 and not start_point_passed:
                    av = 0
                else:
                    av = averager([dp.frequency for dp in window])
                averaged_y.append(av)

            self.mov_av = [DataPoint(year=p, frequency=f) for p, f in
                           zip([d.year for d in self.interpolated()],
                           averaged_y)]
            return self.mov_av

    def mean_average(self, ignoreZeroes=True):
        if ignoreZeroes == True:
            return averager([d.frequency for d in self.moving_average()
                             if d.frequency > 0])
        else:
            return averager([d.frequency for d in self.moving_average()])

    def max_frequency(self, averaged=True):
        if averaged == True:
            return max([d.frequency for d in self.moving_average()])
        else:
            return max([d.frequency for d in self.interpolated()])

    def max_year(self, averaged=True):
        f = self.max_frequency(averaged=averaged)
        if averaged == True:
            datapoints = self.moving_average()
        else:
            datapoints = self.interpolated()
        matches = [d.year for d in datapoints if d.frequency == f]
        try:
            return matches[0]
        except IndexError:
            return 0

    def min_frequency(self, averaged=True):
        if averaged == True:
            return min([d.frequency for d in self.moving_average()])
        else:
            return min([d.frequency for d in self.interpolated()])

    def min_year(self, averaged=True):
        f = self.min_frequency(averaged=averaged)
        if averaged == True:
            datapoints = self.moving_average()
        else:
            datapoints = self.interpolated()
        matches = [d.year for d in datapoints if d.frequency == f]
        try:
            return matches[0]
        except IndexError:
            return 0

    def average_frequency(self, range=(1970, 2000,)):
        vals = [dp.frequency for dp in self.interpolated()
                if dp.year >= range[0] and dp.year <= range[1]]
        if vals:
            return averager(vals)
        else:
            return 0

    def ingest(self, other):
        if other is not None:
            for year, dp in self.data().items():
                if year in other.data():
                    dp.ingest(other.data()[year])


class DataPoint(object):

    def __init__(self, year=None, frequency=None):
        if frequency is None or not frequency or frequency < 0:
            frequency = float(0)
        self.freq = float(frequency)
        self.year = year

    @property
    def frequency(self):
        return self.freq

    def log_frequency(self):
        return calculate_log_frequency(self.frequency)

    def show_label(self):
        if self.year in (1800, 1900, 2000):
            return True
        else:
            return False

    def band(self):
        return log_band(self.frequency)

    def ingest(self, other):
        if other is not None:
            self.freq += other.freq


def calculate_log_frequency(frequency):
    if frequency > 0:
        return log10(frequency)
    else:
        return None

def log_band(frequency):
    if frequency > 0:
        band = int(mathfloor(log10(frequency)))
        if band >= 3:
            band = 3
        band = abs(band - 4)
        if band > 7:
            band = 7
    else:
        band = 8
    return band

def midpoint(label):
    try:
        return midpoints[label]
    except KeyError:
        start, end = parse_label(label)
        midpoints[label] = int(averager((start, end,)))
        return midpoints[label]

def averager(vals):
    if len(vals) > 0:
        return float(sum(vals)) / len(vals)
    else:
        return 0

