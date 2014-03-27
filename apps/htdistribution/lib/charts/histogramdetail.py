
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from django.http import HttpResponse
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

from ...models import CountSet

figure_size = (20, 12)


class HistogramDetail(object):

    def __init__(self):
        pass

    def draw_histogram(self, elements, thesclass_id):
        for e in elements:
            try:
                cset = e.countset_set.get(thesaurusclass__id=thesclass_id)
            except CountSet.DoesNotExist:
                cset = None
            if cset:
                size = cset.branchtotal
                fraction = cset.fraction()
            else:
                size = 0
                fraction = float(0)
            e.bsize = size
            e.fraction = fraction
            if e.fraction == 0:
                e.xunits = 0
            else:
                e.xunits = e.bsize / e.fraction

        if len(elements) < 10:
            total_width = 0.1 * len(elements)
        else:
            total_width = float(1)
        lower_left = 0.5 * (1-total_width)
        maxy = max([e.fraction for e in elements]) * 1.1

        # Calculate the unit length along the x-axis (so that the height
        #  of each bar will be proportional to fraction, and the area will
        #  be proportional to size)
        widest = max([e.xunits for e in elements])
        for e in elements:
            e.xunits = max(e.xunits, widest/10)
        total_xunits = sum([e.xunits for e in elements])
        xunit = float(total_width) / total_xunits

        # set up figure and axis
        self.fig = Figure(figsize=figure_size, facecolor="white")
        self.ax = self.fig.add_subplot(111)

        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, maxy)
        self.ax.set_ylabel("Fraction of all senses")
        self.ax.set_xticks([])

        unitwidth = total_width / len(elements)
        for e in elements:
            width = e.xunits * xunit
            r = Rectangle((lower_left, 0), width, e.fraction, facecolor=e.color,
                            edgecolor="k")
            self.ax.add_patch(r)

            self.ax.annotate("%s (%d)" % (e.label, e.bsize),
            xy = (lower_left, e.fraction), xytext = (10, -10),
            textcoords = 'offset points', ha = 'left', va = 'top',
            bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow',
            alpha = 0.7, zorder=5),)

            lower_left += width

        self._draw_average_line(elements)

        response = HttpResponse(content_type='image/png')
        canvas = FigureCanvasAgg(self.fig)
        canvas.print_png(response)
        return response


    def _draw_average_line(self, elements):
        avg = sum([e.fraction for e in elements]) / len(elements)
        l = Line2D((0, 1), (avg, avg), linestyle="--")
        self.ax.add_line(l)

