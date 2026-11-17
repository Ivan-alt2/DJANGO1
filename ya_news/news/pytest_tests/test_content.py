from http import HTTPStatus

import pytest
from django.conf import settings
from django.urls import reverse

from news.models import Comment

pytestmark = pytest.mark.django_db

HOME_URL = reverse('news:home')


def test_news_count(client, news_list):
    """На главной не больше NEWS_COUNT_ON_HOME_PAGE новостей."""
    response = client.get(HOME_URL)

    object_list = response.context['object_list']

    assert response.status_code == HTTPStatus.OK
    assert len(object_list) <= settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_list):
    """Новости отсортированы от самой свежей к самой старой."""
    response = client.get(HOME_URL)

    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)

    assert all_dates == sorted_dates


def test_comments_order(client, news, author):
    """Комментарии на странице новости идут от старых к новым."""
    for index in range(10):
        Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {index}',
        )

    detail_url = reverse('news:detail', args=(news.pk,))
    response = client.get(detail_url)

    comments = response.context['news'].comment_set.all()
    all_timestamps = [comment.created for comment in comments]
    sorted_timestamps = sorted(all_timestamps)

    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, news):
    """Анонимному пользователю форма комментария не передаётся."""
    detail_url = reverse('news:detail', args=(news.pk,))

    response = client.get(detail_url)

    assert response.status_code == HTTPStatus.OK
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news):
    """Авторизованному пользователю доступна форма комментария."""
    detail_url = reverse('news:detail', args=(news.pk,))

    response = author_client.get(detail_url)

    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
