from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, FormMixin
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from django_celery_beat.models import PeriodicTask
from .models import Feed, FeedArticle, FeedArticleComments
from .forms import NewRssFeedForm, NewFeedArticleCommentForm, ToggleBookmarkForm


class ArticleListView(ListView):
    model = FeedArticle
    ordering = ['-published_at']
    template_name = 'feeds/list.html'
    page_title = 'Feeds'

    def get_queryset(self):
        return FeedArticle\
            .get_with_bookmarked_field_qs(self.request.user)\
            .all()\
            .order_by('-published_at')

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

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx['is_bookmark_page'] = True
        return ctx

    def get_queryset(self):
        user = self.request.user
        return FeedArticle.list_bookmarked(user)


class AddRssFeedView(FormView):
    template_name = 'feeds/new_feed.html'
    form_class = NewRssFeedForm
    success_url = '/'

    def get_context_data(self):
        ctx = super().get_context_data()
        links = Feed.objects.filter(users=self.request.user).values_list('rss_link', flat=True)
        ctx['tasks'] = PeriodicTask.objects.filter(name__in=links).order_by('name')
        return ctx

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

    def get_success_url(self):
        # FIXME: replace with reverse
        return '/articles/{}/'.format(self.object.id)

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

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)


@require_POST
@login_required
def toggle_bookmark_view(request, pk):
    data = request.POST.copy()
    data['user'] = request.user.id
    data['article'] = pk

    form = ToggleBookmarkForm(data)
    if form.is_valid():
        form.toggle()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'errors': form.errors})


@require_POST
@login_required
def resume_feed_update(request, pk):
    task = get_object_or_404(PeriodicTask, pk=pk)
    has_feed = Feed.objects.filter(rss_link=task.name, users=request.user).exists()
    if not has_feed:
        return HttpResponseForbidden()
    task.enabled = True
    task.save()
    return JsonResponse({'status': 'success'})
