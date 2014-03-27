import math
from collections import defaultdict
from matplotlib.patches import Rectangle

from .treemap import Treemap

class TreemapStack(Treemap):

    def draw_treemap(self, elements, **kwargs):
        tax_level = kwargs.get("level", 2)
        mode = kwargs.get("mode", "size")

        # ensure that elements are in a list, and have a color
        try:
            elements[0]
        except IndexError:
            elements = [elements]
        for e in elements:
            try:
                e.color
            except AttributeError:
                e.color = "#CC0000"

        # collect the relevant series of countsets
        # (1 per element per thesaurus class)
        class_counts = defaultdict(list)
        for element in elements:
            for cset in element.countsets(level=tax_level):
                class_counts[cset.thesaurusclass.id].append(cset)

        # Sort the countset series, and add as an attribute ('sortedcounts')
        # to their respective thesaurus classes
        rectangles = []
        for c in [c for c in self.rectangles.values() if c.level == tax_level]:
            if c.id in class_counts:
                class_counts[c.id].sort(key=lambda cset: cset.element.alphasort)
                c.sortedcounts = class_counts[c.id]
                rectangles.append(c)

        if rectangles:
            unitsquare = calculate_unitsquare(rectangles, mode)
            for c in rectangles:
                right_edge = c.inner_rectangle()[0][0] + c.inner_rectangle()[1]
                lower_left = [c.inner_rectangle()[0][0], c.inner_rectangle()[0][1]]
                for j in c.sortedcounts:
                    col = j.element.color
                    if mode == "size":
                        val = j.branchtotal
                    elif mode == "share":
                        val = j.share()
                    height = c.inner_rectangle()[2]
                    width = (val * unitsquare) / height
                    if lower_left[0] + width > right_edge:
                        # Don't colour outside the lines!
                        width = right_edge - lower_left[0]
                    r = Rectangle(lower_left, width, height,
                        facecolor=col, edgecolor='w', zorder=3, alpha=0.7)
                    self.ax.add_patch(r)
                    lower_left[0] += width

        self.draw_key(elements)
        return self._png_response()

def calculate_unitsquare(rectangles, mode):
    def summed_density(area, counts, mode):
        if mode == "size":
            hits = sum([t.branchtotal for t in counts])
        elif mode  == "share":
            hits = sum([t.share() for t in counts])
        return hits / area

    # find the highest-density rectangle
    rectangles = filter_rectangles(rectangles, threshold=0.2)
    rectangles.sort(key=lambda c: summed_density(c.inner_area(),
        c.sortedcounts, mode), reverse=True)
    hd = rectangles[0]

    # calculate unit square based on thehighest-density rectangle
    if mode == "size":
        hits = sum([t.branchtotal for t in hd.sortedcounts])
    elif mode == "share":
        hits = sum([t.share() for t in hd.sortedcounts])
    return hd.inner_area() / hits

def filter_rectangles(rectangles, threshold=1):
    mean_area = sum([r.inner_area() for r in rectangles]) / len(rectangles)
    rectangles = [r for r in rectangles if r.inner_area() > mean_area * threshold]
    return rectangles


