from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import get_object_or_404

from blog.models import Post, Category
from blog.forms import PostForm


class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    extra_context = {'selected': 'home'}

    def get_queryset(self):
        return Post.published.all()


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    extra_context = {'selected': 'detail'}


class PostCreateView(UserPassesTestMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_create.html'
    extra_context = {'selected': 'create_post'}

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        """ Передаем пользователя в форму """
        form.instance.user = self.request.user
        return super().form_valid(form)


class PostUpdateView(UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_create.html'
    selected = 'create_post'
    extra_context = {'selected': 'create_post'}

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        return Post.objects.filter(slug=self.kwargs['slug']).select_related('cat', 'user')


class ByCategoryListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'

    def get_queryset(self):
        cat = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.filter(cat=cat)
