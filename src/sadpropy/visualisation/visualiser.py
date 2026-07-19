import matplotlib.pyplot as plt
import numpy as np

__all__ = ["Visualisation"]

class Visualisation:
    def __init__(self, modeldata):
        self._modeldata = modeldata

    # Helper 

    def plot_line_connectivity(self, show_labels=True):
        point_objects = self._modeldata.point_objects
        line_objects = self._modeldata.line_objects
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection="3d")

        ax.set_title("Line Connectivity")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")

        coords = point_objects.coords

        # --------------------------------------------------------
        # Draw line elements
        # --------------------------------------------------------
        for line_idx in line_objects.index:

            i_node, j_node = line_objects.end_points_idx[line_idx]

            p1 = coords[i_node]
            p2 = coords[j_node]

            ax.plot(
                [p1[0], p2[0]],
                [p1[1], p2[1]],
                [p1[2], p2[2]],
                color="steelblue",
                linewidth=2,
            )

            if show_labels:
                c = line_objects.centroids[line_idx]

                ax.text(
                    c[0],
                    c[1],
                    c[2],
                    line_objects.unique_name[line_idx],
                    fontsize=8,
                    color="black",
                )

        # --------------------------------------------------------
        # Equal aspect ratio
        # --------------------------------------------------------
        mins = coords.min(axis=0)
        maxs = coords.max(axis=0)

        centre = (mins + maxs) / 2
        radius = np.max(maxs - mins) / 2

        ax.set_xlim(centre[0] - radius, centre[0] + radius)
        ax.set_ylim(centre[1] - radius, centre[1] + radius)
        ax.set_zlim(centre[2] - radius, centre[2] + radius)

        plt.tight_layout()
        plt.show()