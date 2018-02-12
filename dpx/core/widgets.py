from datetimewidget import widgets as base_widgets
from django.utils.safestring import mark_safe
from uuid import uuid4


class DateTimeWidget(base_widgets.DateTimeWidget):
    pass
    # def render(self, name, value, attrs=None):
    #     final_attrs = self.build_attrs(attrs)
    #     rendered_widget = super(base_widgets.PickerWidgetMixin, self).render(
    #         name, value, final_attrs
    #     )
    #
    #     options_list = []
    #     for key, value in iter(self.options.items()):
    #         if key in ('autoclose',):
    #             continue
    #
    #         if key == 'language':
    #             key = 'locale'
    #
    #         options_list.append(
    #             '%s: %s' % (key, base_widgets.quote(key, value))
    #         )
    #
    #     js_options = ',\n'.join(options_list)
    #     id = final_attrs.get('id', uuid4().hex)
    #     clearBtn = base_widgets.quote(
    #         'clearBtn',
    #         self.options.get('clearBtn', 'true')
    #     ) == 'true'
    #
    #     return mark_safe(
    #         base_widgets.BOOTSTRAP_INPUT_TEMPLATE[
    #             self.bootstrap_version
    #         ] % dict(
    #             id=id,
    #             rendered_widget=rendered_widget,
    #             clear_button=base_widgets.CLEAR_BTN_TEMPLATE[
    #                 self.bootstrap_version
    #             ] if clearBtn else '',
    #             glyphicon=self.glyphicon,
    #             options=js_options
    #         )
    #     )
