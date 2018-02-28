from django.conf import settings as site_settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files import File
from django.urls import reverse, NoReverseMatch
from django.utils.translation import ugettext_lazy as _
from redis import StrictRedis
from ... import ADMIN_MENU_ITEMS


class AdminViewMixin(LoginRequiredMixin):
    menu_item_name = None

    def get_menu_item_name(self):
        return self.menu_item_name

    def get_menu_items(self):
        item_name = self.get_menu_item_name()

        def r(urlname):
            try:
                return reverse(urlname)
            except NoReverseMatch:
                return 'javascript:;'

        for (name, title, urlname) in ADMIN_MENU_ITEMS:
            yield {
                'title': _(title),
                'url': r('admin_%s' % urlname),
                'selected': item_name and item_name == name
            }

    def get_context_data(self, **kwargs):
        context = super(AdminViewMixin, self).get_context_data(**kwargs)
        context['menu_items'] = self.get_menu_items
        return context


class FileFormMixin(object):
    file_fields = ()

    def get_form_kwargs(self):
        kwargs = super(FileFormMixin, self).get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            redis = StrictRedis.from_url(site_settings.REDIS_URL)
            data = self.request.POST.dict()
            files = self.request.FILES.dict()

            for field in self.file_fields:
                if not field in files and field in data:
                    key = 'tempfile_%s' % data.pop(field)

                    if key in redis:
                        files[field] = File(open(redis[key], 'rb'))
                        del redis[key]

            kwargs.update(
                {
                    'data': data,
                    'files': files
                }
            )

        return kwargs
