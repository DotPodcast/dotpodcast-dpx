from django.shortcuts import get_object_or_404
from ..models import Podcast
from ..forms.podcasts import SubscribeForm, DownloadForm
from .. import exceptions
from .base import JsonView, FormMixin


class PodcastMixin(object):
    def dispatch(self, request, podcast_slug, *args, **kwargs):
        self.podcast = get_object_or_404(Podcast, slug=podcast_slug)
        return super(PodcastMixin, self).dispatch(
            request, *args, **kwargs
        )


class FeedView(PodcastMixin, JsonView):
    def get(self, request):
        page = request.GET.get('page', '1')
        response = self.response()
        self.podcast.dump_json(
            response,
            page=page,
            ssl=request.is_secure()
        )

        return response


class SubscribeView(PodcastMixin, FormMixin, JsonView):
    http_method_names = ('post',)
    form_class = SubscribeForm

    def form_valid(self, form):
        form.subscribe(self.podcast)
        return self.object_as_dict(form)


class DownloadView(PodcastMixin, FormMixin, JsonView):
    form_class = DownloadForm

    def get_request_data(self):
        token = self.request.GET.get('sub')
        jwt = self.request.GET.get('jwt')

        if not jwt:
            raise exceptions.InvalidTokenError(
                'jwt missing'
            )

        if not token:
            raise exceptions.InvalidTokenError(
                'sub missing'
            )

        from jwt import decode
        from jwt.exceptions import InvalidTokenError
        from django.contrib.sites.models import Site

        site = Site.objects.get_current()
        for subscriber in self.podcast.subscribers.filter(
            source_token=token
        ):
            try:
                return decode(
                    jwt,
                    subscriber.secret_token,
                    audience=site.domain
                )
            except InvalidTokenError as ex:
                raise exceptions.InvalidTokenError(
                    str(ex)
                )

        raise exceptions.InvalidTokenError(
            'jwt or sub invalid'
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
