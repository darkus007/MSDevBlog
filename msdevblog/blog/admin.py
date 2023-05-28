from django.contrib import admin

from blog.models import Category, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']  # поля для отображения
    list_filter = ['title']    # правая боковая панель для фильтрации по этим полям
    search_fields = ['title']   # поиск по этим полям
    prepopulated_fields = {'slug': ('title',)}  # автозаполнение slug по title


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'user', 'time_created', 'time_updated', 'status']  # поля для отображения
    list_filter = ['status', 'time_created', 'time_updated', 'user']    # правая боковая панель для фильтрации
    search_fields = ['title', 'body']   # поиск по этим полям
    prepopulated_fields = {'slug': ('title',)}  # автозаполнение slug по title
    raw_id_fields = ['user']  # поисковый виджет вместо выпадающего списка авторов
    date_hierarchy = 'time_updated'  # навигация по датам (размещены под поиском)
    ordering = ['status', 'time_updated']    # порядок сортировки при отображении


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'body', 'time_created']  # поля для отображения
    search_fields = ['post', 'user']  # поиск по этим полям
    ordering = ['time_created', 'post', 'user']  # порядок сортировки при отображении
