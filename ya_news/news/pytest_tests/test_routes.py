from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db

HOME_URL = reverse('news:home')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')


def test_home_availability_for_anonymous_user(client):
    """Главная страница доступна анонимному пользователю."""
    response = client.get(HOME_URL)
    assert response.status_code == HTTPStatus.OK


def test_detail_availability_for_anonymous_user(client, news):
    """Страница отдельной новости доступна анонимному пользователю."""
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, kwargs',
    (
        ('news:delete', pytest.lazy_fixture('pk_for_kwargs')),
        ('news:edit', pytest.lazy_fixture('pk_for_kwargs')),
    ),
)
def test_pages_availability_for_auth_user(author_client, name, kwargs):
    """Страницы редактирования и удаления комментария доступны его автору."""
    url = reverse(name, args=(kwargs['pk'],))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, kwargs',
    (
        ('news:delete', pytest.lazy_fixture('pk_for_kwargs')),
        ('news:edit', pytest.lazy_fixture('pk_for_kwargs')),
    ),
)
def test_redirects(client, name, kwargs):
    """Анонимного пользователя на edit/delete редиректит на страницу входа."""
    url = reverse(name, args=(kwargs['pk'],))
    expected_url = f'{LOGIN_URL}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('vasua_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    'name, kwargs',
    (
        ('news:delete', pytest.lazy_fixture('pk_for_kwargs')),
        ('news:edit', pytest.lazy_fixture('pk_for_kwargs')),
    ),
)
def test_pages_availability_for_different_users(
    parametrized_client, name, kwargs, expected_status
):
    """Редактировать и удалять комментарий может только его автор."""
    url = reverse(name, args=(kwargs['pk'],))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (HOME_URL, LOGIN_URL, SIGNUP_URL)
)
def test_pages_availability_for_anonymous_user(client, url):
    """Публичные страницы доступны анонимному пользователю."""
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_logout(author_client):
    """POST-запрос на страницу выхода возвращает статус 200."""
    response = author_client.post(LOGOUT_URL)
    assert response.status_code == HTTPStatus.OK
