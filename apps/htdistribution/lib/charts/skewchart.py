
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from django.http import HttpResponse
from matplotlib.patches import Circle

figure_size = (20, 12)
volume_multiplier = 50000
xlabel = u"\u00ab more uniform\u2014\u2014   chi-2 statistic (level %d)   \u2014\u2014less uniform \u00bb"
ylabel = "phi coefficient"

class SkewChart(object):

    def __init__(self):
        pass

    def draw_skewchart(self, elements, level=3):
        if level == 2:
            self.datapoints = [(e.chistat2, e.phi(level=2), e.size, e.label, e.color)
                for e in elements]
        elif level == 3:
            self.datapoints = [(e.chistat3, e.phi(level=3), e.size, e.label, e.color)
                for e in elements]

        # set up figure and axis
        self.fig = Figure(figsize=figure_size, facecolor="white")
        self.ax = self.fig.add_subplot(111)

        rangex = max([d[0] for d in self.datapoints]) - min([d[0] for d in self.datapoints])
        minx = min([d[0] for d in self.datapoints]) - (rangex * 0.2)
        maxx = max([d[0] for d in self.datapoints]) + (rangex * 0.2)
        maxy = max([d[1] for d in self.datapoints]) * 1.2
        maxvol = max([d[2] for d in self.datapoints])

        self.ax.set_xlim(minx, maxx)
        self.ax.set_ylim(0, maxy)
        self.ax.set_xlabel(xlabel % level)
        self.ax.set_ylabel(ylabel)

        volume_coefficient = (float(1) / maxvol) * volume_multiplier
        xseries = [d[0] for d in self.datapoints]
        yseries = [d[1] for d in self.datapoints]
        volumes = [d[2] * volume_coefficient for d in self.datapoints]
        colors = [d[4] for d in self.datapoints]
        self.ax.scatter(xseries, yseries, s=volumes, facecolor=colors, alpha=0.9)

        for x, y, volume, label, col in self.datapoints:
            self.ax.annotate(label,
                xy = (x, y), xytext = (-20, 0),
                textcoords = 'offset points', ha = 'right', va = 'center',
                bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow',
                alpha = 0.7, zorder=5),)


        response = HttpResponse(content_type='image/png')
        canvas = FigureCanvasAgg(self.fig)
        canvas.print_png(response)
        return response
