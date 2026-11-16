import pytest
from django.conf import settings
from django.test import Client

from news.models import Comment, News

COMMENT_TEXT = 'Текст комментария'


@pytest.fixture
def author(django_user_model):
    """Автор новости и комментариев."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    """Клиент, авторизованный как автор."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def vasua(django_user_model):
    """Пользователь, не являющийся автором комментария."""
    return django_user_model.objects.create(username='Вася')


@pytest.fixture
def vasua_client(vasua):
    """Клиент, авторизованный как не-автор."""
    client = Client()
    client.force_login(vasua)
    return client


@pytest.fixture
def news():
    """Одна новость в базе."""
    return News.objects.create(title='Заголовок новости', text='Просто текст.')


@pytest.fixture
def news_list():
    """NEWS_COUNT_ON_HOME_PAGE + 1 новость для проверки лимита главной."""
    batch = [
        News(title=f'Новость {index}', text='Просто текст.')
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(batch)


@pytest.fixture
def comment(news, author):
    """Комментарий к новости от лица автора."""
    return Comment.objects.create(
        news=news,
        author=author,
        text=COMMENT_TEXT,
    )


@pytest.fixture
def pk_for_kwargs(comment):
    """Словарь с pk комментария для параметризации в test_routes."""
    return {'pk': comment.pk}
