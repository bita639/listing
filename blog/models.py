from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.


class ActiveArticleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)


class Article(models.Model):
    title = models.CharField(max_length=150)
    author = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='user_articles')
    image = models.ImageField(
        upload_to="blog/%Y/%m/%d/", blank=True, null=True)
    content = models.TextField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)

    objects = models.Manager()
    active_objects = ActiveArticleManager()

    @property
    def short_description(self):
        return self.content if len(self.content) < 35 else (self.content[:33] + '..')

    def __str__(self):
        return self.title
