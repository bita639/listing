from django.shortcuts import render
from .models import Article
from django.views import generic, View

# Create your views here.


class ArticleListView(generic.ListView):
    model = Article
    paginate_by = 8
    context_object_name = 'article_list'
    template_name = 'blog/home.html'

    def get_queryset(self):
        article_list = Article.active_objects.select_related('author').all()

        return article_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Blog'
        return context


class SingleArticleView(generic.DetailView):
    model = Article
    context_object_name = 'article'
    template_name = 'blog/single.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        return context
