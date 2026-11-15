from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class CommonSetUp(TestCase):
    """Базовый класс: пользователи, клиенты и заметки создаются один раз."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Тьюринг')
        cls.reader = User.objects.create(username='Мария Кьюри')

        cls.author_client = TestCase.client_class()
        cls.author_client = cls.client_class()
        cls.author_client.force_login(cls.author)

        cls.reader_client = cls.client_class()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author
        )
        cls.another_note = Note.objects.create(
            title='Радиация',
            text='Первая женщина, которая её открыла',
            author=cls.reader,
        )


class TestContent(CommonSetUp):
    LIST_URL = reverse('notes:list')

    def test_individual_note_in_context(self):
        """На странице списка отображается заметка автора."""
        response = self.author_client.get(self.LIST_URL)

        object_list = response.context['object_list']

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.note, object_list)

    def test_forg_not_org(self):
        """В списке есть только заметки самого пользователя."""
        response = self.reader_client.get(self.LIST_URL)

        object_list = response.context['object_list']

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.another_note, object_list)
        self.assertNotIn(self.note, object_list)


class TestEditNote(CommonSetUp):
    def setUp(self):
        self.edit_url = reverse('notes:edit', args=(self.note.id,))

    def test_authorized_client_has_form(self):
        """Авторизованному пользователю доступна форма редактирования."""
        response = self.author_client.get(self.edit_url)

        form = response.context['form']

        self.assertIn('form', response.context)
        self.assertIsInstance(form, NoteForm)


class TestAddNote(CommonSetUp):
    def setUp(self):
        self.add_url = reverse('notes:add')

    def test_anonymous_client_has_no_form(self):
        """Анонимному пользователю форма добавления не доступна."""
        response = self.client.get(self.add_url)

        self.assertNotIn('form', response.context)

    def test_authorized_client_has_form(self):
        """Авторизованному пользователю доступна форма добавления."""
        response = self.author_client.get(self.add_url)

        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
