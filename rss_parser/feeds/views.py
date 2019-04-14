from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, FormMixin
from django.views.generic.list import ListView
from .models import FeedArticle, FeedArticleComments
from .forms import NewRssFeedForm, NewFeedArticleCommentForm


class ArticleListView(ListView):
    model = FeedArticle
    ordering = ['-published_at']
    template_name = 'feeds/list.html'
    page_title = 'Feeds'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
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


class AddRssFeedView(FormView):
    template_name = 'feeds/new_feed.html'
    form_class = NewRssFeedForm
    success_url = '/'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        user = self.request.user
        form.save(user)
        return super().form_valid(form)


class ArticleCommentView(FormMixin, DetailView):
    template_name = 'feeds/feed_details.html'
    form_class = NewFeedArticleCommentForm
    model = FeedArticle

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_initial(self):
        initial = super().get_initial()
        initial['user'] = self.request.user
        initial['article'] = self.object
        return initial

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx['comments'] = FeedArticleComments.filter_by_feed_article(self.object)
        return ctx

    def form_valid(self, form):
        user = self.request.user
        form.save(user)
        return super().form_valid(form)
