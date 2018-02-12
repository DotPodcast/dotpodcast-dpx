from django.conf.urls import url
from django.contrib.auth import views as auth
from ..views.admin import dashboard, episodes, pages, blog, settings


urlpatterns = [
    url(r'^$', dashboard.DashboardView.as_view(), name='admin_dashboard'),
    url(r'^login/$', auth.LoginView.as_view(), name='login'),
    url(r'^upload/$', dashboard.FileUploadView.as_view(), name='admin_upload'),
    url(r'^upload/complete/$', dashboard.FileUploadCompleteView.as_view(), name='admin_upload_complete'),
    url(r'^episodes/$', episodes.EpisodeListView.as_view(), name='admin_episode_list'),
    url(r'^episodes/create/$', episodes.CreateEpisodeFormView.as_view(), name='admin_create_episode'),
    url(r'^episodes/(?P<pk>\d+)/$', episodes.UpdateEpisodeFormView.as_view(), name='admin_update_episode'),
    url(r'^episodes/(?P<pk>\d+)/delete/$', episodes.DeleteEpisodeView.as_view(), name='admin_delete_episode'),
    url(r'^pages/$', pages.PageListView.as_view(), name='admin_page_list'),
    url(r'^pages/create/$', pages.CreatePageFormView.as_view(), name='admin_create_page'),
    url(r'^pages/(?P<pk>\d+)/$', pages.UpdatePageFormView.as_view(), name='admin_update_page'),
    url(r'^pages/(?P<pk>\d+)/delete/$', pages.DeletePageView.as_view(), name='admin_delete_page'),
    url(r'^blog/$', blog.BlogPostListView.as_view(), name='admin_blog_post_list'),
    url(r'^blog/create/$', blog.CreateBlogPostFormView.as_view(), name='admin_create_blog_post'),
    url(r'^blog/(?P<pk>\d+)/$', blog.UpdateBlogPostFormView.as_view(), name='admin_update_blog_post'),
    url(r'^blog/(?P<pk>\d+)/delete/$', blog.DeleteBlogPostView.as_view(), name='admin_delete_blog_post'),
    url(r'^settings/$', settings.PodcastFormView.as_view(), name='admin_podcast_settings')
]
