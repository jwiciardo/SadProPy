import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from sadpropy.utility._exceptions import ValidationError

__all__ = ["Visualisation"]

class Visualisation:
    def __init__(self, modeldata):
        self._modeldata = modeldata

        # Colour List
        self._colour_cycle = [
            "blue",
            "red",
            "green",
            "cyan",
            "yellow",
            "magenta",
            "tab:red",
            "tab:blue",
            "tab:green",
            "tab:orange",
            "tab:purple",
            "tab:brown",
            "tab:pink",
            "tab:gray",
            "tab:olive",
            "tab:cyan",
        ]

    # HELPER METHOD
    def _get_line_categories(self, colour_by):
        line_objects = self._modeldata.line_objects
        if colour_by is None:
            return np.full(len(line_objects.index), "Default", dtype="U15")

        sections_list = self._modeldata.sections_list
        materials_list = self._modeldata.materials_list
        categories = np.empty(len(line_objects.index), dtype="U15")
        for i in line_objects.index:
            section = sections_list[line_objects.sec_class[i]]
            material = materials_list[section.mats_class[line_objects.sec_idx[i]][0]]
            if colour_by == "Section":
                categories[i] = section.sec_name[line_objects.sec_idx[i]]
            elif colour_by == "Element Type":
                categories[i] = section.element_type[line_objects.sec_idx[i]]
            elif colour_by == "Material":
                categories[i] = material.mat_name[section.mats_idx[line_objects.sec_idx[i]][0]]
            else:
                raise ValidationError(f"Unknown colour_by='{colour_by}'"
                    "Choose from None, 'Section', 'Material', or 'Element Type'"
                )
        return categories

    def _build_colour_map(self, categories):
        unique_categories = np.unique(categories)
        colour_map = {}
        for i, category in enumerate(unique_categories):
            colour_map[category] = self._colour_cycle[i % len(self._colour_cycle)]
        return colour_map
    
    def _get_line_colour(self, line_idx, categories, colour_map):
        category = categories[line_idx]
        return colour_map[category]
    
    def _build_legend(self, ax, colour_map, title):
        handles = []
        for category, colour in colour_map.items():
            handles.append(Line2D([0], [0], color=colour, lw=3, label=category))
        ax.legend(handles=handles, title=title, loc="upper left", bbox_to_anchor=(1.02, 1.0),)

    def plot_line_connectivity(self, show_labels=True, colour_by=None):
        point_objects = self._modeldata.point_objects
        line_objects = self._modeldata.line_objects
        categories = self._get_line_categories(colour_by)
        colour_map = self._build_colour_map(categories)

        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection="3d")
        ax.set_title("Line Connectivity")
        ax.set_xlabel("X", labelpad=5)
        ax.set_ylabel("Y", labelpad=5)
        ax.set_zlabel("Z", labelpad=5)

        ax.tick_params(axis="x", pad=5)
        ax.tick_params(axis="y", pad=5)
        ax.tick_params(axis="z", pad=5)
        coords = point_objects.coords
        mins = coords.min(axis=0)
        maxs = coords.max(axis=0)
        model_size = np.max(maxs - mins)

        # --------------------------------------------------------
        # Draw point objects
        # --------------------------------------------------------
        ax.scatter(
            coords[:, 0],
            coords[:, 1],
            coords[:, 2],
            s=20,
            color="black",
            marker="o",
            label="Points",
            zorder=5,
        )

        # --------------------------------------------------------
        # Draw line elements
        # --------------------------------------------------------
        for line_idx in line_objects.index:
            i_node, j_node = line_objects.end_points_idx[line_idx]
            p1 = coords[i_node]
            p2 = coords[j_node]
            color = self._get_line_colour(
                line_idx=line_idx,
                categories=categories,
                colour_map=colour_map,
            )
            ax.plot(
                [p1[0], p2[0]],
                [p1[1], p2[1]],
                [p1[2], p2[2]],
                color=color,
                linewidth=2,
            )
            if show_labels:
                offset_size = model_size * 0.01
                label_position = (
                    line_objects.centroids[line_idx]
                    + offset_size
                )
                ax.text(
                    *label_position,
                    line_objects.unique_name[line_idx],
                    fontsize=8,
                    color="black",
                )

        # --------------------------------------------------------
        # Equal aspect ratio
        # --------------------------------------------------------
        padding = model_size * 0.05

        ax.set_xlim(mins[0] - padding, maxs[0] + padding)
        ax.set_ylim(mins[1] - padding, maxs[1] + padding)
        ax.set_zlim(mins[2], maxs[2] + padding)

        ax.set_box_aspect((
            maxs[0] - mins[0],
            maxs[1] - mins[1],
            maxs[2] - mins[2],
        ))

        if colour_by is not None:
            self._build_legend(
                ax=ax,
                colour_map=colour_map,
                title=colour_by.replace("_", " ").title(),
            )
        plt.tight_layout()
        plt.show()