from django.shortcuts import render
from django.views.generic import ListView, DetailView

from blog.models import Post


def index(request):
    return render(request, 'blog/base.html')


class ContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected'] = self.selected
        return context


class PostListView(ContextMixin, ListView):
    model = Post
    template_name = 'blog/post_list.html'
    selected = 'home'

    def get_queryset(self):
        return Post.published.all()

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['selected'] = 'home'
    #     return context


class PostDetailView(ContextMixin, DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    selected = 'detail'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['selected'] = 'detail'
    #     return context

