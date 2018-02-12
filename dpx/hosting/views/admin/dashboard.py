from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse
from django.views.generic.base import TemplateView, View
from redis import StrictRedis
from tempfile import mkstemp
import json
import os
from . import AdminViewMixin


class DashboardView(AdminViewMixin, TemplateView):
    template_name = 'hosting/admin/dashboard.html'
    menu_item_name = 'dashboard'


class FileUploadView(LoginRequiredMixin, View):
    http_method_names = ('post',)

    def post(self, request):
        redis = StrictRedis.from_url(settings.REDIS_URL)
        guid = request.POST['qquuid']
        data = request.FILES['qqfile']
        part_index = int(request.POST['qqpartindex'])
        total_parts = int(request.POST['qqtotalparts'])
        key = 'tempfile_%s' % guid

        if key not in redis:
            filename = request.POST['qqfilename']
            handle, filename = mkstemp(
                suffix=os.path.splitext(filename)[-1]
            )

            os.write(handle, data.read())
            redis[key] = filename
        else:
            filename = redis[key]
            open(filename, 'a').write(data.read())

        return HttpResponse(
            json.dumps(
                {
                    'guid': guid,
                    'success': True
                }
            ),
            content_type='text/plain'
        )


class FileUploadCompleteView(LoginRequiredMixin, View):
    def post(self, request):
        pass
