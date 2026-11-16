from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()

LOGIN_URL = reverse('users:login')
SUCCESS_URL = reverse('notes:success')


class CommonSetUp(TestCase):
    """Общая подготовка: пользователи, клиенты и заметки создаются один раз."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Тьюринг')
        cls.reader = User.objects.create(username='Мария Кьюри')

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='zagolovok',
            author=cls.author,
        )
        cls.another_note = Note.objects.create(
            title='Радиация',
            text='Первая женщина, которая её открыла',
            slug='radiatsiya',
            author=cls.reader,
        )
