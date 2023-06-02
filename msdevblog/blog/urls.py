from django.urls import path
from blog.views import *

app_name = 'blog'

urlpatterns = [
    path('', PostListView.as_view(), name='home'),
    path('new-post/', PostCreateView.as_view(), name='post-new'),
    path('update-post/<slug:slug>/', PostUpdateView.as_view(), name='post-update'),
    path('by-category/<slug:slug>/', ByCategoryListView.as_view(), name='category'),
    path('by-tag/<slug:slug>/', ByTagListView.as_view(), name='tag'),
    path('feedback/', feedback, name='feedback'),
    path('<slug:slug>/', post_detail, name='post-detail'),
]
