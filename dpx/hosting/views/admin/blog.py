from django.conf import settings
from django.core.files import File
from django.core.urlresolvers import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.utils.translation import ugettext_lazy as _
from redis import StrictRedis
from . import AdminViewMixin, FileFormMixin
from ...models import BlogPost
from ...forms.blog import BlogPostForm


class BlogPostListView(AdminViewMixin, ListView):
    model = BlogPost
    template_name = 'hosting/admin/blog_post_list.html'
    menu_item_name = 'blog_posts'

    def get_query_set(self):
        return super(BlogPostListView, self).get_query_set().live()


class BlogPostFormMixin(FileFormMixin, AdminViewMixin):
    model = BlogPost
    template_name = 'hosting/admin/blog_post_form.html'
    menu_item_name = 'blog_posts'
    form_class = BlogPostForm
    file_fields = ('banner_image',)

    def get_query_set(self):
        return super(BlogPostFormMixin, self).get_query_set().live()

    def get_success_url(self):
        return reverse('admin_update_blog_post', args=[self.object.pk])


class CreateBlogPostFormView(BlogPostFormMixin, CreateView):
    pass


class UpdateBlogPostFormView(BlogPostFormMixin, UpdateView):
    pass


class DeleteBlogPostView(BlogPostFormMixin, DeleteView):
    template_name = 'hosting/admin/blog_post_delete.html'

    def get_success_url(self):
        return reverse('admin_blog_post_list')
