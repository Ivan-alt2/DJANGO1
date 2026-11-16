from http import HTTPStatus

import pytest

from news.models import Comment, News

pytestmark = pytest.mark.django_db

ANONYMOUS_COMMENT_TEXT = 'Комментарий от анонима'
AUTHOR_COMMENT_TEXT = 'Комментарий от пользователя'
FORBIDDEN_TEXT = 'негодяй редиска'
EDITED_COMMENT_TEXT = 'Коммент отредоктироваван атором'


def test_anonymous_user_cannot_comment(client, news, url):
    """Аноним не может отправить комментарий: редирект на логин, записи нет."""
    news_count_before = News.objects.count()

    response = client.post(url, data={'text': ANONYMOUS_COMMENT_TEXT})

    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(
        news=news.pk, text=ANONYMOUS_COMMENT_TEXT
    ).exists()
    assert News.objects.count() == news_count_before


def test_authenticated_user_can_comment(author_client, news, author, url):
    """Авторизованный пользователь может оставить комментарий."""
    response = author_client.post(url, data={'text': AUTHOR_COMMENT_TEXT})

    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.filter(
        news=news.pk, author=author, text=AUTHOR_COMMENT_TEXT
    ).exists()


def test_comment_warring_text_for_authenticated_user(author_client, news, url):
    """За запрещённое слово форма возвращает ошибку, комментарий не создаётся."""
       response = client.post(
        NEWS_DETAIL_URL,
        data={'text': ANONYMOUS_COMMENT_TEXT},
    )


    assert response.status_code == HTTPStatus.OK

    form = response.context['form']

    assert 'text' in form.errors
    assert 'Не ругайтесь!' in form.errors['text']


def test_authenticated_user_can_edit_comment(
    author_client, comment, author, edit_url
):
    """Автор может отредактировать свой комментарий."""
    form_data = {
        'news': comment.news.pk,
        'author': author.pk,
        'text': EDITED_COMMENT_TEXT,
    }

    response = author_client.post(edit_url, data=form_data)

    assert response.status_code == HTTPStatus.FOUND

    comment.refresh_from_db()

    assert Comment.objects.filter(
        news=comment.news.pk,
        author=author,
        text=EDITED_COMMENT_TEXT,
    ).exists()


def test_authenticated_user_can_delete_comment(
    author_client, comment, news, delete_url
):
    """Автор может удалить свой комментарий."""
    news_count_before = News.objects.count()
    comment_count_before = Comment.objects.count()

    response = author_client.post(delete_url)

    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(pk=comment.pk).exists()
    assert News.objects.count() == news_count_before
    assert Comment.objects.count() == comment_count_before - 1


def test_authenticated_user_cannot_edit_comment(
    vasua_client, comment, edit_url
):
    """Посторонний пользователь не может редактировать чужой комментарий."""
    comment_count_before = Comment.objects.count()

    response = vasua_client.post(edit_url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comment_count_before


def test_authenticated_user_cannot_delete_comment(
    vasua_client, comment, delete_url
):
    """Посторонний пользователь не может удалить чужой комментарий."""
    comment_count_before = Comment.objects.count()

    response = vasua_client.post(delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comment_count_before
