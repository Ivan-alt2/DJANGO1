from http import HTTPStatus

from django.urls import reverse

from notes.forms import NoteForm
from notes.tests.common import LOGIN_URL, CommonSetUp


class TestContent(CommonSetUp):
    LIST_URL = reverse('notes:list')

    def test_individual_note_in_context(self):
        """На странице списка отображается заметка автора."""
        response = self.author_client.get(self.LIST_URL)

        object_list = response.context['object_list']

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(self.note, object_list)

    def test_forg_not_org(self):
        """В списке есть только заметки самого пользователя."""
        response = self.reader_client.get(self.LIST_URL)

        object_list = response.context['object_list']

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(self.another_note, object_list)
        self.assertNotIn(self.note, object_list)


class TestEditNote(CommonSetUp):
    def setUp(self):
        self.edit_url = reverse('notes:edit', args=(self.note.slug,))

    def test_authorized_client_has_form(self):
        """Авторизованному пользователю доступна форма редактирования."""
        response = self.author_client.get(self.edit_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)


class TestAddNote(CommonSetUp):
    def setUp(self):
        self.add_url = reverse('notes:add')

    def test_anonymous_client_has_no_form(self):
        """Анонимного пользователя страница добавления редиректит на логин."""
        response = self.client.get(self.add_url)

        self.assertRedirects(response, f'{LOGIN_URL}?next={self.add_url}')

    def test_authorized_client_has_form(self):
        """Авторизованному пользователю доступна форма добавления."""
        response = self.author_client.get(self.add_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
