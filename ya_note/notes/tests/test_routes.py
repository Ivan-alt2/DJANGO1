from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()

HOME_URL = reverse('notes:home')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
LIST_URL = reverse('notes:list')


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель простой')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', slug=1, author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.id,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.id,))
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))

    def test_pages_availability(self):
        """Страницы доступны соответствующим типам клиентов."""
        users_statuses = (
            (None, self.client, (HOME_URL, LOGIN_URL, SIGNUP_URL)),
            (self.author, self.author_client, (ADD_URL, LIST_URL, SUCCESS_URL)),
            (self.author, self.author_client, (self.edit_url, self.delete_url)),
        )
        for user, client, urls in users_statuses:
            for url in urls:
                with self.subTest(user=user, url=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_delete_detail(self):
        """Edit/delete/detail доступны автору и недоступны другим."""
        clients_statuses = (
            ('author', self.author_client, HTTPStatus.OK),
            ('reader', self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for username, client, status in clients_statuses:
            for name, url in (
                ('edit', self.edit_url),
                ('delete', self.delete_url),
                ('detail', self.detail_url),
            ):
                with self.subTest(user=username, name=name, status=status):
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects_for_anonymous_client(self):
        """Анонимные запросы к приватным страницам ведут на логин."""
        urls = (
            self.edit_url,
            self.delete_url,
            self.detail_url,
            ADD_URL,
            LIST_URL,
            SUCCESS_URL,
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_logout(self):
        """POST-запрос на страницу выхода возвращает статус 200."""
        response = self.author_client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
