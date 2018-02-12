from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from . import AdminViewMixin
from ...forms.importing import ImportForm


class CreateImportView(AdminViewMixin, FormView):
    template_name = 'hosting/admin/import_form.html'
    form_class = ImportForm

    def get_success_url(self):
        return reverse('admin_import_progress')

    def form_valid(self, form):
        response = super(CreateImportView, self).form_valid(form)
        form.save()

        messages.success(
            self.request,
            _('Your import has started.')
        )

        return response

class ImportDetailView(AdminViewMixin, TemplateView):
    template_name = 'hosting/admin/import_detail.html'
