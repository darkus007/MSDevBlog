from .models import Category, Post, BlogTag


def categories(request):
    """ Добавляет информацию о категориях в контекст """
    _categories = Category.objects.values('title', 'slug')
    return {'categories': _categories}


def new_posts(request):
    """ Добавляет информацию о пяти новых постах в контекст """
    _new_posts = Post.published.values('title', 'slug').order_by('-time_updated')[:5]
    return {'new_posts': _new_posts}


def tags_list(request):
    """ Добавляет информацию о тегах в контекст """
    _tags = BlogTag.objects.all()
    return {'tags_list': _tags}
