from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.list import ListView
from .models import FeedArticle


class ArticleListView(ListView):
    model = FeedArticle
    ordering = ['-published_at']
    template_name = 'feeds/list.html'
    page_title = 'Feeds'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self,  **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = self.page_title
        return ctx


class SubscribedArticlesListView(ArticleListView):
    page_title = 'My Feeds'

    def get_queryset(self):
        user = self.request.user
        return FeedArticle.list_user_feed_items(user)


class BookmarkedArticlesListView(ArticleListView):
    page_title = 'Bookmarks'

    def get_queryset(self):
        user = self.request.user
        return FeedArticle.list_bookmarked(user)
