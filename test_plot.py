import numpy as np
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection="3d")
title = "Test"
coords = np.asarray([[0.0, 0.0, 0.0], [0.5, 0.0, 0.0]], dtype=np.float64)
ax.scatter(
    coords[:, 0], coords[:, 1], coords[:, 2],
    s=12.0,
    c="black",
    marker="o",
    depthshade=True,
    zorder=1,
)
ax.quiver(
    0.0, 0.0, 0.0,
    0.5, 0.0, 0.0,
    color="red",
    linewidth=1.2,
    zorder=10,
)

plt.tight_layout()
plt.show()