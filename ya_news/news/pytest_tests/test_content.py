from http import HTTPStatus

import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

pytestmark = pytest.mark.django_db

HOME_URL = reverse('news:home')


def test_home_page_news_count(client, news_list):
    """На главной не больше settings.NEWS_COUNT_ON_HOME_PAGE новостей."""
    response = client.get(HOME_URL)
    assert response.status_code == HTTPStatus.OK
    assert (
        len(response.context['object_list']) == settings.NEWS_COUNT_ON_HOME_PAGE
    )


def test_home_page_news_order(client, news_list):
    """Новости на главной отсортированы по дате."""
    response = client.get(HOME_URL)

    news_list = response.context['object_list']
    sorted_news = sorted(news_list, key=lambda news: news.date)

    assert list(news_list) == list(sorted_news)


def test_comments_order_on_news_detail(client, comment):
    """Комментарии на странице новости идут от старых к новым."""
    url = reverse('news:detail', args=(comment.news.pk,))
    response = client.get(url)

    comment_list = response.context['object'].comment_set.all()

    assert list(comment_list) == list(comment_list.order_by('created'))


def test_comment_form_unavailable_for_anonymous_user(client, news):
    """Анонимному пользователю форма комментария не показывается."""
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert not isinstance(response.context.get('form'), CommentForm)


def test_comment_form_available_for_authenticated_user(author_client, news):
    """Авторизованному пользователю доступна форма комментария."""
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.context['form'], CommentForm)
