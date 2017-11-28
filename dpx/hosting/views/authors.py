from django.views.generic.detail import DetailView
from ..models import Author


class AuthorDetailView(DetailView):
    model = Author
