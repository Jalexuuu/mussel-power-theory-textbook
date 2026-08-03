import json

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np

LAYOUT_FILE = "src/img/layout.json"

BASE_COLOURS = [
    mcolors.to_rgb(c)
    for c in [
        "#FFC900",
        "#FF0002",
        "#FF7000",
        "#B700FF",
        "#7E89FF",
        "#00E2FF",
        "#00FF47",
        "#B4FF00",
    ]
]


def desaturate(rgb, amount):
    hsv = mcolors.rgb_to_hsv(np.array(rgb).reshape(1, 1, 3))[0][0]
    hsv[1] = max(0.0, hsv[1] - amount)
    return mcolors.hsv_to_rgb(hsv)


with open(LAYOUT_FILE, "r", encoding="utf-8") as f:
    layout = json.load(f)


def build_rings(bank_masks):
    rings = [[], [], []]

    for mask_num in sorted((k for k in bank_masks if k.isdigit()), key=int):
        n = str(mask_num)

        rings[0].append(bank_masks[n])
        rings[1].extend([bank_masks[n + "l"], bank_masks[n + "r"]])
        rings[2].extend([bank_masks[n + "L"], bank_masks[n + "R"]])

    return rings


def ring_colours(base_colours):
    middle = []
    outer = []

    for colour in base_colours:
        middle.extend([desaturate(colour, 0.25), desaturate(colour, 0.30)])
        outer.extend([desaturate(colour, 0.45), desaturate(colour, 0.50)])

    return [base_colours, middle, outer]


RINGS = [(0.0, 0.5), (0.5, 1.0), (1.0, 1.5)]

VARIANTS = [
    ("all", [0, 1, 2]),
    ("inner", [0]),
    ("middle", [0, 1]),
]

for bank, bank_masks in layout.items():
    rings = build_rings(bank_masks)

    colours = ring_colours(BASE_COLOURS)

    for suffix, indices in VARIANTS:
        fig, ax = plt.subplots(figsize=(8, 8))

        for i in indices:
            layer = rings[i]
            inner, outer = RINGS[i]

            wedges, _ = ax.pie(
                [1] * len(layer),
                radius=outer,
                colors=colours[i],
                startangle=112.5,
                counterclock=False,
                wedgeprops={
                    "width": outer - inner,
                    "edgecolor": "white",
                },
            )

            radius = (inner + outer) / 2

            for wedge, label in zip(wedges, layer):
                angle_rad = np.deg2rad((wedge.theta1 + wedge.theta2) / 2)

                ax.text(
                    radius * np.cos(angle_rad),
                    radius * np.sin(angle_rad),
                    label,
                    ha="center",
                    va="center",
                    fontsize=24,
                    fontweight="bold",
                )

        ax.set_aspect("equal")
        plt.tight_layout()

        output_file = f"src/img/{bank}_joystick_pie.svg"
        if suffix != "all":
            output_file = f"src/img/{bank}_joystick_{suffix}_pie.svg"

        plt.savefig(output_file, dpi=300, bbox_inches="tight", transparent=True)

        # for a zoomed in diagram of just the inner ring
        if suffix == "inner":

            plt.savefig(
                f"src/img/{bank}_joystick_inner_pie_cropped.svg",
                dpi=300,
                bbox_inches="tight",
                pad_inches=-2,
                transparent=True,
            )

        plt.close(fig)

        print(f"saved {output_file} ^^")
