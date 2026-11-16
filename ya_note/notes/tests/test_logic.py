from http import HTTPStatus

from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.common import SUCCESS_URL, CommonSetUp


class TestCommentEditDelete(CommonSetUp):
    NOTE_TITLE_NEW = 'Текст комментария'
    NOTE_TEXT_NEW = 'Обновлённый комментарий'
    NOTE_SLUG_NEW = '4'

    def setUp(self):
        self.edit_url = reverse('notes:edit', args=(self.note.slug,))
        self.delete_url = reverse('notes:delete', args=(self.note.slug,))
        self.add_url = reverse('notes:add')
        self.form_data = {
            'title': self.NOTE_TITLE_NEW,
            'text': self.NOTE_TEXT_NEW,
            'slug': self.NOTE_SLUG_NEW,
        }

    def assert_note_attributes(self, note):
        self.assertEqual(self.note.text, note.text)
        self.assertEqual(self.note.title, note.title)
        self.assertEqual(self.note.slug, note.slug)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        Note.objects.exclude(pk=self.note.pk).delete()

        response = self.author_client.delete(self.delete_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Посторонний пользователь не может удалить чужую заметку."""
        Note.objects.exclude(pk__in=(self.note.pk, self.another_note.pk)).delete()

        response = self.reader_client.delete(self.delete_url)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 2)

    def test_author_can_edit_note(self):
        """Автор может отредактировать свою заметку."""
        note_count = Note.objects.count()

        response = self.author_client.post(self.edit_url, data=self.form_data)

        self.assertRedirects(response, SUCCESS_URL)
        self.note.refresh_from_db()

        updated_note = Note.objects.get(pk=self.note.pk)
        self.assert_note_attributes(updated_note)
        self.assertEqual(Note.objects.count(), note_count)

    def test_user_cant_edit_note_of_another_user(self):
        """Посторонний пользователь не может редактировать чужую заметку."""
        note_count = Note.objects.count()

        response = self.reader_client.post(self.edit_url, data=self.form_data)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()

        updated_note = Note.objects.get(pk=self.note.pk)
        self.assert_note_attributes(updated_note)
        self.assertEqual(Note.objects.count(), note_count)

    def test_logged_in_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        Note.objects.all().delete()

        response = self.author_client.post(self.add_url, data=self.form_data)

        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)

    def test_anonymous_user_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        Note.objects.all().delete()

        response = self.client.post(self.add_url, data=self.form_data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), 0)

    def test_cannot_create_note_with_duplicate_slug(self):
        """Нельзя создать заметку с занятым slug."""
        Note.objects.all().delete()
        Note.objects.create(
            title='Существующая',
            text='Текст',
            slug=self.NOTE_SLUG_NEW,
            author=self.author,
        )

        bad_note = {
            'title': self.NOTE_TITLE_NEW,
            'text': self.NOTE_TEXT_NEW,
            'slug': self.NOTE_SLUG_NEW,
        }

        response = self.author_client.post(self.add_url, data=bad_note)

        self.assertFormError(
            response.context['form'],
            field='slug',
            errors=f'{self.NOTE_SLUG_NEW}{WARNING}',
        )
        self.assertEqual(Note.objects.count(), 1)


class NoteCreationTestCase(CommonSetUp):
    NOTE_TEXT = 'Новый текст'
    NOTE_TITLE = 'Новый заголовок'

    def test_create_note_with_auto_slug(self):
        """Если slug не указан, он генерируется из заголовка."""
        Note.objects.all().delete()
        form_data = {'text': self.NOTE_TEXT, 'title': self.NOTE_TITLE}

        response = self.author_client.post(
            reverse('notes:add'), data=form_data
        )

        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.latest('id')
        expected_slug = slugify(form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_empty_slug(self):
        """Пустой slug заменяется на slug, сгенерированный из заголовка."""
        Note.objects.all().delete()
        form_data = {
            'text': self.NOTE_TEXT,
            'title': self.NOTE_TITLE,
            'slug': '',
        }

        response = self.author_client.post(
            reverse('notes:add'), data=form_data
        )

        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.latest('id')
        expected_slug = slugify(form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
