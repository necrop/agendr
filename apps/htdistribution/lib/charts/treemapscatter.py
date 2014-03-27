import random
from collections import defaultdict

from .treemap import Treemap

# sizes and colours of datapoint dots
dots = (("major", 6, "#FF0000"), ("minor", 3, "#FF0000"), ("subs", 3, "#FF0000"))

# shades of orange, getting lighter
tint_shades = ("#FF9900", "#FFA011", "#FFA723", "#FFAE35", "#FFB547",
                "#FFBC59", "#FFC36A", "#FFCA7C", "#FFD18E", "#FFD8A0",
                "#FFE0B2",)

# maximum number of points to show on a treemap
maximum_points = 10000


class TreemapScatter(Treemap):

    def draw_treemap(self, element):
        self._add_tints(element.rank_countsets(level=3, mode="density",
            skipSmallClasses=True, threshold=200)[:10])
        self._add_series(element.countsets())
        self.draw_key((element,))
        return self._png_response()

    def _add_series(self, countsets):
        points_list = []
        for countset in countsets:
            thes_id = countset.thesaurusclass.id
            for i in range(countset.majorsenses):
                points_list.append((thes_id, "major"))
            for i in range(countset.minorsenses):
                points_list.append((thes_id, "minor"))
            for i in range(countset.subentries):
                points_list.append((thes_id, "subs"))
        # Randomly sample, if > 10000 data points
        if len(points_list) > maximum_points:
            points_list = random.sample(points_list, maximum_points)

        distribution = defaultdict(list)
        for thes_id, t in points_list:
            distribution[thes_id].append(t)

        series = {"major": {"x": [], "y": []},
                  "minor": {"x": [], "y": []},
                  "subs": {"x": [], "y": []},}
        for thes_id, vals in distribution.items():
            c = self.rectangles[thes_id]
            for t in vals:
                x, y = self._random_point(c)
                series[t]["x"].append(x)
                series[t]["y"].append(y)

        for t, dotsize, color in dots:
            self.ax.scatter(series[t]["x"], series[t]["y"],
                            s=dotsize, facecolor=color, edgecolor="none",
                            zorder=4)

    def _add_tints(self, countsets):
        for i, countset in enumerate(countsets):
            try:
                color = tint_shades[i]
            except IndexError:
                color = tint_shades[-1]
            self._add_rectangle(countset.thesaurusclass, facecolor=color,
                alpha=0.5)
