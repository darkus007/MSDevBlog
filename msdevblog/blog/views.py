from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.views.generic import ListView, CreateView, UpdateView
from django.shortcuts import get_object_or_404, render

from blog.models import Post, Category, Comment
from blog.forms import PostForm, CommentForm


class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    extra_context = {'selected': 'home'}

    def get_queryset(self):
        return Post.published.all()


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.method == 'POST' and request.user.is_authenticated and request.user.is_email_activated:
        form = CommentForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.instance.post = post
            form.save()

    form = CommentForm()
    comments = Comment.objects.filter(post=post)
    is_author = bool(request.user == post.user)
    return render(request, 'blog/post_detail.html',
                  {'object': post, 'form': form, 'comments': comments, 'is_author': is_author})


class PostCreateView(UserPassesTestMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_create.html'
    extra_context = {'selected': 'create_post'}

    def test_func(self):
        return self.request.user.is_authenticated

    def form_valid(self, form):
        """ Передаем пользователя в форму """
        if not self.request.user.is_email_activated:
            raise ValidationError("Пользователь не подтвердил e-mail!")
        form.instance.user = self.request.user
        return super().form_valid(form)


class PostUpdateView(UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_create.html'
    extra_context = {'selected': 'create_post'}

    def test_func(self):
        post_owner = Post.objects.get(slug=self.kwargs['slug'])
        return bool(self.request.user.is_authenticated and post_owner.user == self.request.user)

    def get_queryset(self):
        return Post.objects.filter(slug=self.kwargs['slug']).select_related('cat', 'user')


class ByCategoryListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'

    def get_queryset(self):
        cat = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.published.filter(cat=cat)
