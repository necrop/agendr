import random

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from django.http import HttpResponse

from ...models import ThesaurusClass


figure_size = (20, 12)
key_height = 0.04

# Alternating colours for the three main branches
base_colors = {
    1: ("#E5FFE5", "#EDFFED"),
    122209: ("#E8FFFF", "#EFFFFF"),
    153072: ("#FFDBFF", "#FFE5FF")# ("#FFFFE5", "#FFFFED")
}


class Treemap(object):

    def __init__(self, **kwargs):
        self._load_rectangles()
        self._setup_figure()
        self.show_labels2 = kwargs.get("labels2", True)
        self.show_labels3 = kwargs.get("labels3", True)

    def _png_response(self):
        self._add_labels()
        response = HttpResponse(content_type='image/png')
        canvas = FigureCanvasAgg(self.fig)
        canvas.print_png(response)
        return response

    def _setup_figure(self):
        # set up figure and axis
        self.fig = Figure(figsize=figure_size, facecolor="white")
        self.ax = self.fig.add_subplot(111)
        self.fig.tight_layout()

        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.get_xaxis().set_ticks([])
        self.ax.get_yaxis().set_ticks([])
        # Draw rectangles for each thesaurus class
        self._draw_rectangles()

    def _load_rectangles(self):
        # Draw the rectangle coordinates for each class branch
        self.rectangles = {}
        for c in ThesaurusClass.objects.all():
            self.rectangles[c.id] = c

    def _draw_rectangles(self):
        # Draw the rectangles for each class branch
        for level in (2, 3, 1):
            for c in [c for c in self.rectangles.values() if c.level == level]:
                if c.level == 2:
                    color = base_colors[c.superordinate.id][c.count % 2]
                else:
                    color = 'none'
                if level == 1:
                    self._add_rectangle(c, facecolor=color, edgecolor="k")
                else:
                    self._add_rectangle(c, facecolor=color)

    def _add_labels(self):
        # Add text label for each level-2 branch
        if self.show_labels2:
            for c in [c for c in self.rectangles.values() if c.level == 2]:
                self.ax.text(c.originx + 0.005, c.originy + (c.height / 2),
                             c.label, zorder=5, fontsize="xx-large",
                             color="#000000", alpha=0.8)
        # Add text label for each level-3 branch (if the box is big enough)
        if self.show_labels3:
            for c in [c for c in self.rectangles.values() if c.level == 3 and
                        c.height > 0.04 and c.width > 0.02]:
                box = c.inner_rectangle()
                # bbox is used to clip text that might run over the edge
                bbox = Rectangle(box[0], box[1], box[2], transform=self.ax.transData)
                self.ax.text(box[0][0], box[0][1] + 0.002,
                             c.label, zorder=5, fontsize="small",
                             color="#000000", alpha=1, clip_path=bbox,)

    def _add_rectangle(self, c, **kwargs):
        facecolor = kwargs.get("facecolor", "none")
        edgecolor = kwargs.get("edgecolor", "#cccccc")
        alpha = kwargs.get("alpha", 1)
        r = Rectangle((c.originx, c.originy), c.width, c.height,
                       edgecolor=edgecolor, facecolor=facecolor, alpha=alpha)
        self.ax.add_patch(r)

    def _random_point(self, c, **kwargs):
        if kwargs.get("inner"):
            r = c.inner_rectangle()
            x = random.uniform(r[0][0], r[0][0] + r[1])
            y = random.uniform(r[0][1], r[0][1] + r[2])
        else:
            x = random.uniform(c.originx, c.originx + c.width)
            y = random.uniform(c.originy, c.originy + c.height)
        return (x, y)

    def draw_key(self, elements):
        if len(elements) == 1:
            self.ax.text(0.5, key_height/2, elements[0].label,
                        color="k", ha="center")
        else:
            components = []
            components.append(("Key:", "w", 0, 0.1))

            unitwidth = float(0.9) / max(len(elements), 5)
            lower_left = 0.1
            for element in elements:
                components.append((element.label, element.color, lower_left,
                                unitwidth))
                lower_left += unitwidth

            for c in components:
                r = Rectangle((c[2], 0), c[3], key_height,
                            edgecolor="k", facecolor=c[1], zorder=6)
                self.ax.add_patch(r)

                # bbox is used to clip text that might run over the edge
                bbox = Rectangle((c[2], 0), c[3], key_height,
                            transform=self.ax.transData)
                self.ax.text(c[2] + (c[3]/10), key_height/2,
                             c[0], zorder=7, color="k", clip_path=bbox,)
