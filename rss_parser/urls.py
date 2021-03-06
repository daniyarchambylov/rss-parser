from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from rss_parser.accounts import views as account_views
from rss_parser.feeds import views as feed_views

urlpatterns = [
    path('login/', LoginView.as_view(template_name='accounts/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', account_views.RegistrationView.as_view(), name='registration'),
    path('my-feeds/', feed_views.SubscribedArticlesListView.as_view(), name='my-feeds'),
    path('bookmarks/', feed_views.BookmarkedArticlesListView.as_view(), name='bookmarks'),
    path('settings/', feed_views.AddRssFeedView.as_view(), name='settings-page'),
    path('articles/<int:pk>/', feed_views.ArticleCommentView.as_view(), name='feed-article-detail'),
    path('toggle-bookmark/<int:pk>/', feed_views.toggle_bookmark_view, name='toggle-bookmark'),
    path('resume-feed-update/<int:pk>/', feed_views.resume_feed_update, name='resume-feed-update'),
    path('', feed_views.ArticleListView.as_view(), name='home'),
]
