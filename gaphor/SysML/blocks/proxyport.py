from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import AttachedPresentation, Named
from gaphor.diagram.shapes import (
    Box,
    IconBox,
    Text,
    TextAlign,
    VerticalAlign,
    draw_border,
)
from gaphor.diagram.support import represents
from gaphor.SysML import sysml
from gaphor.UML.recipes import stereotypes_str


def text_position(position):
    return {
        "text-align": TextAlign.LEFT if position == "left" else TextAlign.RIGHT,
        "vertical-align": VerticalAlign.BOTTOM
        if position == "bottom"
        else VerticalAlign.TOP,
    }


@represents(sysml.ProxyPort)
class ProxyPortItem(Named, AttachedPresentation[sysml.ProxyPort]):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=16, height=16)
        self.watch("subject[NamedElement].name").watch(
            "subject[TypedElement].type.name"
        ).watch("show_type")

    show_type: attribute[int] = attribute("show_type", int, default=False)

    def update_shapes(self):
        self.shape = IconBox(
            Box(draw=draw_border),
            Text(
                text=lambda: stereotypes_str(
                    self.subject, [self.diagram.gettext("proxy")]
                )
            ),
            Text(text=self._format_name),
            style=text_position(self.connected_side()),
        )

    def _format_name(self):
        if not self.subject:
            return ""

        name = self.subject.name or ""
        if self.show_type and self.subject.type:
            return f"{name}: {self.subject.type.name or ''}"
        return name
