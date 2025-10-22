"""Majority vote gate item definition."""

from math import pi

from gaphas.geometry import Rectangle

from gaphor.core.modeling import DrawContext
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    from_package_str,
)
from gaphor.diagram.shapes import Box, IconBox, Text, stroke
from gaphor.diagram.support import represents
from gaphor.diagram.text import FontStyle, FontWeight
from gaphor.RAAML import raaml
from gaphor.RAAML.fta.constants import DEFAULT_FTA_MAJOR, DEFAULT_FTA_MINOR
from gaphor.UML.recipes import stereotypes_str

DEFAULT_WIDTH = 40


@represents(raaml.MAJORITY_VOTE)
class MajorityVoteItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=DEFAULT_WIDTH, height=DEFAULT_FTA_MAJOR)

        self.watch("subject[NamedElement].name").watch(
            "subject[NamedElement].namespace.name"
        )

    def update_shapes(self, event=None):
        self.shape = IconBox(
            Box(
                draw=draw_majority_vote_gate,
            ),
            Text(
                text=lambda: stereotypes_str(
                    self.subject, [self.diagram.gettext("Majority Vote Gate")]
                ),
            ),
            Text(
                text=lambda: self.subject.name or "",
                width=lambda: self.width - 4,
                style={
                    "font-weight": FontWeight.BOLD,
                    "font-style": FontStyle.NORMAL,
                },
            ),
            Text(
                text=lambda: from_package_str(self),
                style={"font-size": "x-small"},
            ),
        )


def draw_majority_vote_gate(box, context: DrawContext, bounding_box: Rectangle):
    cr = context.cairo
    left = 0
    right = bounding_box.width
    wall_top = bounding_box.height / 3.0
    wall_bottom = bounding_box.height

    # Left wall
    cr.move_to(left, wall_bottom)
    cr.line_to(left, wall_top)

    # Right wall
    cr.move_to(right, wall_bottom)
    cr.line_to(right, wall_top)

    # Top arc
    rx = right - left
    ry = bounding_box.height * 2.0 / 3.0
    cr.move_to(left, wall_top)
    cr.save()
    cr.translate(left + rx / 2.0, wall_top)
    cr.scale(rx / 2.0, ry / 2.0)
    cr.arc(0.0, 0.0, 1.0, pi, 0)
    cr.restore()

    # Bottom arc
    ry = bounding_box.height / 4.0
    cr.move_to(left, wall_bottom)
    cr.save()
    cr.translate(left + rx / 2.0, wall_bottom)
    cr.scale(rx / 2.0, ry / 2.0)
    cr.arc(0.0, 0.0, 1.0, pi, 0)
    cr.restore()

    # Draw "m"
    text = "m"
    if bounding_box.height > 3 * bounding_box.width:
        cr.set_font_size(32 * bounding_box.width / DEFAULT_WIDTH)
    elif bounding_box.width > 3 * bounding_box.height:
        cr.set_font_size(40 * bounding_box.height / DEFAULT_FTA_MAJOR)
    else:
        cr.set_font_size(
            17
            * (bounding_box.width + bounding_box.height)
            / (DEFAULT_FTA_MINOR + DEFAULT_FTA_MAJOR)
        )
    x_bearing, y_bearing, width, height, x_advance, y_advance = cr.text_extents(text)
    x = bounding_box.width / 2.0 - (width / 2 + x_bearing)
    y = bounding_box.height / 2.0 - (height / 2 + y_bearing)
    cr.move_to(x, y)
    cr.show_text(text)

    stroke(context, fill=True)
