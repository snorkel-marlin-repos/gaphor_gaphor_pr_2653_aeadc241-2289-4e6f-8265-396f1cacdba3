from gaphor import UML
from gaphor.core.format import format, parse
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    help_link,
    unsubscribe_all_on_destroy,
)
from gaphor.transaction import transactional
from gaphor.UML.classes.association import AssociationItem
from gaphor.UML.classes.classespropertypages import new_builder
from gaphor.UML.profiles.stereotypepropertypages import stereotype_model


def _dummy_handler(*args):
    pass


@PropertyPages.register(AssociationItem)
class AssociationPropertyPage(PropertyPageBase):
    NAVIGABILITY = (None, False, True)
    AGGREGATION = ("none", "shared", "composite")

    order = 20

    def __init__(self, item):
        self.item = item
        self.subject = item.subject
        self.watcher = item.subject and self.subject.watcher()
        self.semaphore = 0

    def handlers_end(self, end_name, end):
        subject = end.subject

        if UML.recipes.get_stereotypes(subject):
            model, toggle_handler, set_value_handler = stereotype_model(subject)
            return model, {
                f"{end_name}-toggle-stereotype": toggle_handler,
                f"{end_name}-set-slot-value": set_value_handler,
            }
        else:
            return None, {
                f"{end_name}-toggle-stereotype": (_dummy_handler,),
                f"{end_name}-set-slot-value": (_dummy_handler,),
            }

    def construct_end(self, builder, end_name, end, stereotypes_model):
        subject = end.subject
        title = builder.get_object(f"{end_name}-title")
        if subject.type:
            title.set_text(f"{end_name.title()} (: {subject.type.name})")

        self.update_end_name(builder, end_name, subject)

        navigation = builder.get_object(f"{end_name}-navigation")
        navigation.set_selected(self.NAVIGABILITY.index(subject.navigability))

        aggregation = builder.get_object(f"{end_name}-aggregation")
        aggregation.set_selected(self.AGGREGATION.index(subject.aggregation))

        if stereotypes_model:
            stereotype_list = builder.get_object(f"{end_name}-stereotype-list")
            stereotype_list.set_model(stereotypes_model)
        else:
            stereotype_frame = builder.get_object(f"{end_name}-stereotype-frame")
            stereotype_frame.set_visible(False)

    def update_end_name(self, builder, end_name, subject):
        name = builder.get_object(f"{end_name}-name")
        new_name = (
            format(
                subject,
                visibility=True,
                is_derived=True,
                multiplicity=True,
            )
            or ""
        )
        if not (name.is_focus() or self.semaphore):
            self.semaphore += 1
            name.set_text(new_name)
            self.semaphore -= 1
        return name

    def construct(self):
        if not self.subject:
            return None

        head = self.item.head_end
        tail = self.item.tail_end

        head_model, head_signal_handlers = self.handlers_end("head", head)
        tail_model, tail_signal_handlers = self.handlers_end("tail", tail)

        builder = new_builder(
            "association-editor",
            "association-info",
            signals={
                "show-direction-changed": (self._on_show_direction_change,),
                "invert-direction-changed": (self._on_invert_direction_change,),
                "head-name-changed": (self._on_end_name_change, head),
                "head-navigation-changed": (self._on_end_navigability_change, head),
                "head-aggregation-changed": (self._on_end_aggregation_change, head),
                "head-info-clicked": (self._on_association_info_clicked,),
                "tail-name-changed": (self._on_end_name_change, tail),
                "tail-navigation-changed": (self._on_end_navigability_change, tail),
                "tail-aggregation-changed": (self._on_end_aggregation_change, tail),
                "tail-info-clicked": (self._on_association_info_clicked,),
                **head_signal_handlers,
                **tail_signal_handlers,
            },
        )

        self.info = builder.get_object("association-info")
        help_link(builder, "head-info-icon", "head-info")
        help_link(builder, "tail-info-icon", "tail-info")

        show_direction = builder.get_object("show-direction")
        show_direction.set_active(self.item.show_direction)

        self.construct_end(builder, "head", head, head_model)
        self.construct_end(builder, "tail", tail, tail_model)

        def name_handler(event):
            end_name = "head" if event.element is head.subject else "tail"
            self.update_end_name(builder, end_name, event.element)

        def restore_nav_handler(event):
            for end_name, end in (("head", head), ("tail", tail)):
                combo = builder.get_object(f"{end_name}-navigation")
                self._on_end_navigability_change(combo, None, end)

        # Watch on association end:
        self.watcher.watch("memberEnd[Property].name", name_handler).watch(
            "memberEnd[Property].visibility", name_handler
        ).watch("memberEnd[Property].lowerValue", name_handler).watch(
            "memberEnd[Property].upperValue", name_handler
        ).watch(
            "memberEnd[Property].type",
            restore_nav_handler,
        )

        return unsubscribe_all_on_destroy(
            builder.get_object("association-editor"), self.watcher
        )

    @transactional
    def _on_show_direction_change(self, button, gparam):
        self.item.show_direction = button.get_active()

    @transactional
    def _on_invert_direction_change(self, button):
        self.item.invert_direction()

    @transactional
    def _on_end_name_change(self, entry, end):
        if not self.semaphore:
            self.semaphore += 1
            parse(end.subject, entry.get_text())
            self.semaphore -= 1

    @transactional
    def _on_end_navigability_change(self, dropdown, _pspec, end):
        if end.subject and end.subject.opposite and end.subject.opposite.type:
            UML.recipes.set_navigability(
                end.subject.association,
                end.subject,
                self.NAVIGABILITY[dropdown.get_selected()],
            )
            # Call this again, or non-navigability will not be displayed
            self.item.update_ends()

    @transactional
    def _on_end_aggregation_change(self, dropdown, _pspec, end):
        end.subject.aggregation = self.AGGREGATION[dropdown.get_selected()]

    def _on_association_info_clicked(self, widget, event):
        self.info.set_relative_to(widget)
        self.info.set_visible(True)
