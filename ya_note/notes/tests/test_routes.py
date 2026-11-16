from http import HTTPStatus

from django.urls import reverse

from notes.models import Note
from notes.tests.common import LOGIN_URL, SUCCESS_URL, CommonSetUp

HOME_URL = reverse('notes:home')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
ADD_URL = reverse('notes:add')
LIST_URL = reverse('notes:list')


class TestRoutes(CommonSetUp):
    def setUp(self):
        self.edit_url = reverse('notes:edit', args=(self.note.slug,))
        self.delete_url = reverse('notes:delete', args=(self.note.slug,))
        self.detail_url = reverse('notes:detail', args=(self.note.slug,))

    def test_pages_availability(self):
        """Страницы доступны соответствующим типам клиентов."""
        public_urls = (HOME_URL, LOGIN_URL, SIGNUP_URL)
        private_urls = (ADD_URL, LIST_URL, SUCCESS_URL)
        note_urls = (self.edit_url, self.delete_url)

        cases = (
            ('anonymous', self.client, public_urls),
            ('author', self.author_client, private_urls),
            ('author', self.author_client, note_urls),
        )
        for username, client, urls in cases:
            for url in urls:
                with self.subTest(user=username, url=url):
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
