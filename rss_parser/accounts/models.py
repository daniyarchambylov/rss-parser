from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    feeds = models.ManyToManyField('feeds.Feed', related_name='users')
    bookmarked_articles = models.ManyToManyField('feeds.FeedArticle', related_name='users')
