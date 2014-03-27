from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from django.http import HttpResponse

figure_size = (12, 6)
xlabel = "year"
ylabel = "frequency (per million)"


class FrequencyPlot(object):

    def __init__(self, lex_item):
        self.lex_item = lex_item

    def draw_chart(self):
        if self.lex_item.level() == "type":
            series, fill = series_from_type(self.lex_item)
            title = "Frequency for %s" % (self.lex_item.identifier())
        elif self.lex_item.level() == "wordclass":
            series, fill = series_from_wordclass(self.lex_item)
            title = "Frequency for %s wordclass" % (
                    self.lex_item.pos_description())
        elif self.lex_item.level() == "entry":
            series, fill = series_from_wordclass(self.lex_item)
            title = "Frequency for %s" % (self.lex_item.label)

        if fill is not None:
            ymax = max(fill[1])
        elif series:
            ymax = max([max(s[1]) for s in series])
        else:
            ymax = 1

        fig = Figure(figsize=figure_size, facecolor="white")
        ax = fig.add_subplot(111)

        ax.set_xlim(1750, 2010)
        ax.set_ylim(0, ymax * 1.2)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(b=True)

        if fill is not None:
            ax.fill_between(fill[0], 0, fill[1], facecolor="#4FD5D6", alpha=0.5)
        for s in series:
            xp = [x for x, y in zip(s[0], s[1]) if y > 0]
            yp = [y for y in s[1] if y > 0]
            ax.plot(xp, yp, "o-", label=s[2])
        ax.legend(loc="upper left", shadow=True)

        response = HttpResponse(content_type='image/png')
        canvas = FigureCanvasAgg(fig)
        canvas.print_png(response)
        return response


def series_from_type(lex_item):
    if lex_item.freq_table() is not None:
        ft = lex_item.freq_table().tools()
        x = [dp.year for dp in ft.moving_average()]
        y = [dp.frequency for dp in ft.moving_average()]
    else:
        x = []
        y = []
    series = [(x, y, lex_item.identifier(),),]
    return (series, None)

def series_from_wordclass(lex_item):
    series = []
    for type in [t for t in lex_item.types() if t.freq_table() is not None]:
        ft = type.freq_table().tools()
        x = [dp.year for dp in ft.moving_average()]
        y = [dp.frequency for dp in ft.moving_average()]
        series.append((x, y, type.identifier(),))

    # Summed frequencies, used to define the filled area
    if series:
        x = [dp.year for dp in lex_item.summed_frequency().moving_average()]
        y = [dp.frequency for dp in lex_item.summed_frequency().moving_average()]
        fill = (x, y,)
    else:
        fill = None

    return (series, fill)

