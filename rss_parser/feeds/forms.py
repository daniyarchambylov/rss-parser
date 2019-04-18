from django.contrib.auth import get_user_model
from django import forms
from .parser import parse, normalize_feed_items
from .models import Feed, FeedArticle, FeedArticleComments


User = get_user_model()


class NewRssFeedForm(forms.Form):
    url = forms.URLField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._parsed_data = None

    def clean_url(self):
        url = self.cleaned_data['url']
        try:
            data = parse(url)
        except:
            raise forms.ValidationError('Format error.')
        self._parsed_data = data
        self._parsed_data['items'] = normalize_feed_items(self._parsed_data['items'])
        return url

    def save(self, user):
        feed = Feed.create_from_feedparser(self._parsed_data)
        user.feeds.add(feed)
        for item in self._parsed_data['items']:
            FeedArticle.create_from_feedparser(feed, item)
        return feed


class NewFeedArticleCommentForm(forms.ModelForm):
    class Meta:
        model = FeedArticleComments
        fields = ['user', 'comment', 'article']
        widgets = {
            'user': forms.HiddenInput(),
            'article': forms.HiddenInput(),
            'comment': forms.Textarea(),
        }


class ToggleBookmarkForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())
    article = forms.ModelChoiceField(queryset=FeedArticle.objects.all())

    def toggle(self):
        user = self.cleaned_data['user']
        article = self.cleaned_data['article']
        if user.bookmarked_articles.filter(id=article.id).exists():
            user.bookmarked_articles.remove(article)
        else:
            user.bookmarked_articles.add(article)
