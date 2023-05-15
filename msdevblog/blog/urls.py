from django.urls import path
from blog.views import *

app_name = 'blog'

urlpatterns = [
    path('', PostListView.as_view(), name='home'),
    path('<slug:slug>/', PostDetailView.as_view(), name='post-detail'),
]
