from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, UpdateView
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.conf import settings

from msdevblog.settings import PAGINATE_BY_CONST
from .models import Post, Category, Comment, BlogTag
from .forms import PostForm, CommentForm, FeedbackForm
from .utilities import send_feedback_mail


class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    extra_context = {'selected': 'home'}
    paginate_by = PAGINATE_BY_CONST

    def get_queryset(self):
        return Post.published.all()


def post_detail(request, slug):
    post = get_object_or_404(Post.objects, slug=slug)

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


class ByTagListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'

    def get_queryset(self):
        tag = get_object_or_404(BlogTag, slug=self.kwargs['slug'])
        return Post.published.filter(tags__name__in=[tag.name]).distinct()


def feedback(request):
    """ Отправляет сообщение администратору сайта. """
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            send = send_feedback_mail(
                subject=form.cleaned_data['theme'],
                message=form.cleaned_data['text'] + '\nE-mail: ' + form.cleaned_data['email'],
                from_email=settings.SERVER_EMAIL,
                recipient_list=settings.ADMINS
            )
            if send:
                messages.add_message(request, messages.SUCCESS, 'Ваше сообщение отправлено!')
                form = FeedbackForm()
            else:
                messages.add_message(request, messages.SUCCESS, 'Что то пошло не так, попробуйте повторить позже...')
    else:
        form = FeedbackForm()
    return render(request, 'blog/feedback.html', {'form': form, 'selected': 'feedback'})


@require_POST
def search_view(request):
    if request.method == 'POST':
        searched = request.POST['searched']  # <input name="searched" ...
        if not searched:
            return redirect(reverse('blog:home'))

        # Простой поиск по нескольким полям
        # object_list = Post.published.annotate(
        #         search=SearchVector('title', 'body'), ).filter(search=searched)

        # Поиск с выделением основ слов и ранжирование результатов
        # config='russian' - настраиваем удаление русских стоп слов
        search_vector = SearchVector('title', 'body', config='russian')
        search_query = SearchQuery(searched, config='russian')
        object_list = Post.published.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)).filter(search=search_query).order_by('-rank')

        return render(request, 'blog/post_list.html', {'object_list': object_list, 'search_key': searched})
    return render(request, 'blog/post_list.html', {})


def page_not_found(request, exception):
    return render(request, 'blog/base.html')
