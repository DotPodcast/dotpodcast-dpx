from django.shortcuts import get_object_or_404
from ..models import Podcast, TokenPair
from ..forms.podcasts import SubscribeForm, DownloadForm
from .. import exceptions
from .base import JsonView, FormMixin


class PodcastMixin(object):
    def dispatch(self, request, *args, **kwargs):
        self.podcast = get_object_or_404(Podcast)
        return super(PodcastMixin, self).dispatch(
            request, *args, **kwargs
        )


class FeedHeadView(PodcastMixin, JsonView):
    def get(self, request):
        response = self.response()
        self.podcast.dump_head_json(
            response,
            ssl=request.is_secure()
        )

        return response


class FeedBodyView(PodcastMixin, JsonView):
    def get(self, request):
        response = self.response()
        self.podcast.dump_body_json(
            response,
            page=request.GET.get('page', '1'),
            ssl=request.is_secure()
        )

        return response


class SubscribeView(PodcastMixin, FormMixin, JsonView):
    http_method_names = ('options', 'post',)
    form_class = SubscribeForm

    def form_valid(self, form):
        form.subscribe(self.podcast)
        return self.object_as_dict(form)


class DownloadView(PodcastMixin, FormMixin, JsonView):
    form_class = DownloadForm

    def get_request_data(self):
        sub = self.request.GET.get('sub')
        token = self.request.GET.get('jwt')

        if not token:
            raise exceptions.InvalidTokenError('jwt missing')

        if not sub:
            raise exceptions.InvalidTokenError('sub missing')

        from jwt import decode
        from jwt.exceptions import InvalidTokenError

        try:
            pair = TokenPair.objects.get(public_token=sub)
        except TokenPair.DoesNotExist:
            raise exceptions.InvalidTokenError('public_token invalid')

        try:
            return decode(
                token,
                pair.secret_token,
                audience=self.request.get_host()
            )
        except InvalidTokenError as ex:
            raise exceptions.InvalidTokenError(
                str(ex)
            )

    def get_form_kwargs(self):
        return {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
            'data': self.get_request_data()
        }

    def get(self, request, kind):
        form = self.get_form()

        if form.is_valid():
            return form.download(self.podcast, kind)

        return self.form_invalid(form)
