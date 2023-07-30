from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.

# Модель таблицы базы данных Категории


class Category(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название категории')

    def __str__(self):
        return self.title

    # Умная ссылка
    def get_absolute_url(self):
        return reverse('category', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


# Модель таблицы базы данных Статьи
class Article(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название статьи')
    content = models.TextField(verbose_name='Описание статьи')
    photo = models.ImageField(upload_to='photos/', blank=True, null=True, verbose_name='Изображение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изминения')
    views = models.IntegerField(default=0, verbose_name='Просмотры')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    video = models.CharField(max_length=500, verbose_name='Ссылка видео', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор', blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article', kwargs={'pk': self.pk})

    def get_photo(self):
        try:
            return self.photo.url
        except:
            return 'https://mobimg.b-cdn.net/v3/fetch/99/99b1f94e983b079412fd1c56fff58e75.jpeg'

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='Статья')
    text = models.TextField(verbose_name='Коментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    def __str__(self):
        return f'{self.user.username}'

    class Meta:
        verbose_name = 'Коментарий'
        verbose_name_plural = 'Коментарии'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username}'

    def get_photo(self):
        try:
            return self.photo.url
        except:
            return 'https://bootdey.com/img/Content/avatar/avatar7.png'

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
