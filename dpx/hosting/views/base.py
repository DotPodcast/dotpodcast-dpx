from django.http.response import HttpResponse, HttpResponseBase, Http404
from django.views.generic.base import View
from ..exceptions import ViewError, InvalidContentTypeError
import json


class JsonView(View):
    def dispatch(self, request, *args, **kwargs):
        handler = self.http_method_not_allowed

        if request.method.lower() in self.http_method_names:
            if hasattr(self, request.method.lower()):
                handler = getattr(
                    self,
                    request.method.lower()
                )

        try:
            data = handler(request, *args, **kwargs)
        except Http404 as ex:
            data = self.response(
                {
                    'error': str(ex)
                },
                status=404
            )
        except ViewError as ex:
            data = self.response(
                {
                    'error': str(ex)
                },
                status=400
            )

        if isinstance(data, HttpResponseBase):
            return data

        return self.response(data)

    def http_method_not_allowed(self, request, *args, **kwargs):
        return self.response(
            {
                'error': 'Method not allowed',
                'allowed_methods': self._allowed_methods()
            },
            status=405
        )

    def response(self, data=None, status=200):
        response = HttpResponse(
            content_type='application/json',
            status=status
        )

        if data is not None:
            json.dump(data, response)

        return response


class FormMixin(object):
    initial = {}
    form_class = None
    success_url = None
    prefix = None

    def get_initial(self):
        return self.initial.copy()

    def get_prefix(self):
        return self.prefix

    def get_form_class(self):
        return self.form_class

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()

        return form_class(**self.get_form_kwargs())

    def get_request_data(self):
        content_type = self.request.META['CONTENT_TYPE']
        if content_type == 'application/json':
            return json.loads(self.request.body)

        raise InvalidContentTypeError('Invalid content type')

    def get_form_kwargs(self):
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix()
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update(
                {
                    'data': self.get_request_data()
                }
            )

        return kwargs

    def object_as_dict(self, form=None):
        if form:
            return form.instance.as_dict()

    def form_valid(self, form):
        status = 200

        if self.request.method == 'POST':
            status = 201

        return self.response(
            self.object_as_dict(form),
            status=status
        )

    def form_invalid(self, form):
        return self.response(
            {
                'error': 'POST data invalid',
                'detail': form.errors
            },
            status=400
        )

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)

        return self.form_invalid(form)
