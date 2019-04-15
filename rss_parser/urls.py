from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import path
from rss_parser.accounts import views as account_views
from rss_parser.feeds import views as feed_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(template_name='accounts/login.html', redirect_authenticated_user=True), name='login'),
    path('register/', account_views.RegistrationView.as_view(), name='registration'),
    path('my-feeds/', feed_views.SubscribedArticlesListView.as_view(), name='my-feeds'),
    path('bookmarks/', feed_views.BookmarkedArticlesListView.as_view(), name='bookmarks'),
    path('add-feed/', feed_views.AddRssFeedView.as_view(), name='add-rss-feed'),
    path('articles/<int:pk>/', feed_views.ArticleCommentView.as_view(), name='feed-article-detail'),
    path('', feed_views.ArticleListView.as_view(), name='home'),
]
