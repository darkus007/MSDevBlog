from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy
from .models import Post


class LatestPostsFeed(Feed):
    title = 'MS DevBlog'
    link = reverse_lazy('blog:home')
    description = 'Новые посты на сайте MSDevBlog.'

    def items(self):
        return Post.published.all()[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return truncatewords_html(item.body, 30)

    def item_pubdate(self, item):
        return item.time_created
