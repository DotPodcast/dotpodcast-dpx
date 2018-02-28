from django.conf import settings
from django.core.files import File
from django.core.urlresolvers import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.utils.translation import ugettext_lazy as _
from redis import StrictRedis
from . import AdminViewMixin, FileFormMixin
from ...models import Page
from ...forms.pages import PageForm


class PageListView(AdminViewMixin, ListView):
    model = Page
    template_name = 'hosting/admin/page_list.html'
    menu_item_name = 'pages'

    def get_query_set(self):
        return super(PageListView, self).get_query_set().live()


class PageFormMixin(FileFormMixin, AdminViewMixin):
    model = Page
    template_name = 'hosting/admin/page_form.html'
    menu_item_name = 'pages'
    form_class = PageForm
    file_fields = ('banner_image',)

    def get_query_set(self):
        return super(PageFormMixin, self).get_query_set().live()

    def get_success_url(self):
        return reverse('admin_update_page', args=[self.object.pk])


class CreatePageFormView(PageFormMixin, CreateView):
    pass


class UpdatePageFormView(PageFormMixin, UpdateView):
    pass


class DeletePageView(AdminViewMixin, DeleteView):
    menu_item_name = 'pages'
    template_name = 'hosting/admin/page_delete.html'
    model = Page

    def get_query_set(self):
        return super(DeletePageView, self).get_query_set().live()

    def get_success_url(self):
        return reverse('admin_page_list')
