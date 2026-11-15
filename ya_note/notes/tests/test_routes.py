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
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', slug=1, author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.id,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.id,))
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

    def test_home_page(self):
        """Главная страница доступна любому пользователю."""
        response = self.client.get(HOME_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        """Edit/delete/detail доступны автору и недоступны другим."""
        users_statuses = (
            ('author', self.author, HTTPStatus.OK),
            ('reader', self.reader, HTTPStatus.NOT_FOUND),
        )
        for username, user, status in users_statuses:
            self.client.force_login(user)
            for name, url in (
                ('edit', self.edit_url),
                ('delete', self.delete_url),
                ('detail', self.detail_url),
            ):
                with self.subTest(user=username, name=name, status=status):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_note_edit(self):
        """Аноним от страницы edit уходит на логин."""
        redirect_url = f'{LOGIN_URL}?next={self.edit_url}'
        response = self.client.get(self.edit_url)
        self.assertRedirects(response, redirect_url)

    def test_redirect_for_note_delete(self):
        """Аноним от страницы delete уходит на логин."""
        redirect_url = f'{LOGIN_URL}?next={self.delete_url}'
        response = self.client.get(self.delete_url)
        self.assertRedirects(response, redirect_url)

    def test_redirect_for_note_detail(self):
        """Аноним от страницы заметки уходит на логин."""
        redirect_url = f'{LOGIN_URL}?next={self.detail_url}'
        response = self.client.get(self.detail_url)
        self.assertRedirects(response, redirect_url)

    def test_redirect_for_add(self):
        """Аноним от страницы добавления уходит на логин."""
        redirect_url = f'{LOGIN_URL}?next={ADD_URL}'
        response = self.client.get(ADD_URL)
        self.assertRedirects(response, redirect_url)

    def test_redirect_for_list(self):
        """Аноним от списка заметок уходит на логин."""
        redirect_url = f'{LOGIN_URL}?next={LIST_URL}'
        response = self.client.get(LIST_URL)
        self.assertRedirects(response, redirect_url)

    def test_redirect_for_success(self):
        """Аноним от страницы успеха уходит на логин."""
        redirect_url = f'{LOGIN_URL}?next={SUCCESS_URL}'
        response = self.client.get(SUCCESS_URL)
        self.assertRedirects(response, redirect_url)

    def test_login_page_availability(self):
        """Страница входа доступна анонимному пользователю."""
        response = self.client.get(LOGIN_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_signup_page_availability(self):
        """Страница регистрации доступна анонимному пользователю."""
        response = self.client.get(SIGNUP_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout(self):
        """POST-запрос на страницу выхода возвращает статус 200."""
        response = self.auth_client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_add_page_availability(self):
        """Страница добавления заметки доступна авторизованному."""
        response = self.auth_client.get(ADD_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_list_page_availability(self):
        """Список заметок доступен авторизованному пользователю."""
        response = self.auth_client.get(LIST_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_success_page_availability(self):
        """Страница успеха доступна авторизованному пользователю."""
        response = self.auth_client.get(SUCCESS_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
