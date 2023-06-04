import os
from django.core.files.storage import FileSystemStorage
from urllib.parse import urljoin
from datetime import datetime
from django.conf import settings


class CkeditorCustomStorage(FileSystemStorage):
    """
    Изменяем расположение медиа файлов редактора CKEditor.
    Для применения указываем в настройках settings.py:
        CKEDITOR_5_FILE_STORAGE = 'blog.utils.CkeditorCustomStorage'
    """
    location = os.path.join(settings.MEDIA_ROOT, 'uploads/')
    base_url = urljoin(settings.MEDIA_URL, 'uploads/')

    def get_folder_name(self):
        return datetime.now().strftime('%Y/%m/%d')

    def get_valid_name(self, name):
        return name

    def _save(self, name, content):
        folder_name = self.get_folder_name()
        name = os.path.join(folder_name, self.get_valid_name(name))
        return super()._save(name, content)
