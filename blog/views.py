from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .models import Category, Article, Comment, Profile
from .forms import ArticleForm, LoginForm, RegisterForm, CommentForm, ProfileForm, ChgAccountForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib import messages


# Create your views here.

# Функция для главной страницы
# def index(request):
#     articles = Article.objects.all()  # получаем все статьи
#     context = {
#         'title': 'Киномания',
#         'articles': articles
#     }
#     return render(request, 'blog/index.html', context)
#   верни  нарисуй(по запросу,   куда,       что передать)


class ArticleListView(ListView):
    model = Article  # говорим для какой модели
    template_name = 'blog/index.html'  # говорим для какой страницы
    context_object_name = 'articles'  # под каким ключём передаю
    extra_context = {
        'title': 'Киномания'
    }


# -----------------------------------------------------------------------------------------
# Функция возвращает статьи на главную страницу по категории
# def category_view(request, pk):
#     articles = Article.objects.filter(category_id=pk)
#     category = Category.objects.get(pk=pk)
#     context = {
#         'title': f'Ктегория {category.title}',
#         'articles': articles
#     }
#
#     return render(request, 'blog/index.html', context)


class ArticleListByCategory(ArticleListView):
    # Метод возвращает статьи по pk
    def get_queryset(self):
        articles = Article.objects.filter(category_id=self.kwargs['pk'])
        return articles

    # Функия отвечающая за динамическое возвращение данные (для изменеения названия title)
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        category = Category.objects.get(pk=self.kwargs['pk'])
        context['title'] = category.title
        return context


# -----------------------------------------------------------------------------------------
# Функцтя для страницы статьи
# def article_view(request, pk):
#     article = Article.objects.get(pk=pk)
#     context = {
#         'title': f'Статья {article.title}',
#         'article': article
#     }
#     return render(request, 'blog/article_detail.html', context)

class ArticleDetailView(DetailView):
    model = Article
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        article = Article.objects.get(pk=self.kwargs['pk'])
        article.views += 1
        article.save()
        context['title'] = article.title
        if self.request.user.is_authenticated:
            context['comment_form'] = CommentForm()
        context['comments'] = Comment.objects.filter(article=article)
        return context


# -----------------------------------------------------------------------------------------

# Функция для добавления статей
# def add_article(request):
#     if request.method == 'POST':
#         form = ArticleForm(request.POST, request.FILES)
#         if form.is_valid():
#             article = Article.objects.create(**form.cleaned_data)
#             article.save()
#             return redirect('article', article.pk)
#     else:
#         form = ArticleForm()
#     context = {
#         'title': 'Создание статьи',
#         'form': form
#     }
#
#     return render(request, 'blog/add_article.html', context)


class NewArticle(CreateView):
    form_class = ArticleForm
    template_name = 'blog/add_article.html'
    extra_context = {
        'title': 'Создание статьи'
    }

    # функция для автора статьи
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)



class ArticleUpdate(UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blog/add_article.html'


class ArticleDelete(DeleteView):
    model = Article
    context_object_name = 'article'
    success_url = reverse_lazy('index')


def user_login(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            login_form = LoginForm(data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                if user:
                    login(request, user)
                    messages.success(request, 'Успешный вход в Аккаунт')
                    return redirect('index')
                else:
                    messages.warning(request, 'Не верное имя пользователя или пароль')
                    return redirect('login')
            else:
                messages.warning(request, 'Не верное имя пользователя или пароль')
                return redirect('login')
        else:
            login_form = LoginForm()

        context = {
            'title': 'Вход в аккаунт',
            'login_form': login_form
        }

        return render(request, 'blog/login.html', context)
    else:
        return redirect('index')


def user_logout(request):
    logout(request)
    return redirect('index')


#  Класс для поиска статей наследуемся от класса который отвечает за глав страницу
class SearchResults(ArticleListView):
    def get_queryset(self):
        word = self.request.GET.get('q').capitalize()
        articles = Article.objects.filter(title__icontains=word)
        return articles


# Функция для Регистрации пользователя
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            form2 = ProfileForm(request.POST, request.FILES)
            if form2.is_valid():
                profile = form2.save(commit=False)
                profile.user = user
                profile.save()
                messages.success(request, 'Регистрация прошла успешно. Войдите в Аккаунт')
                return redirect('login')
            else:
                for field in form.errors:
                    messages.error(request, form.errors[field].as_text())
                    return redirect('register')
        else:
            for field in form.errors:
                messages.error(request, form.errors[field].as_text())
                return redirect('register')

    else:
        form = RegisterForm()
        form2 = ProfileForm()

    context = {
        'register_form': form,
        'title': 'Регистрация пользователя',
        'form2': form2
    }

    return render(request, 'blog/register.html', context)


def save_comment(request, pk):
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = Article.objects.get(pk=pk)
        comment.user = request.user
        comment.save()
        messages.success(request, 'Ваш комментарий опубликован')
        return redirect('article', pk)


def profile_view(request, pk):
    profile = Profile.objects.get(user_id=pk)
    articles = Article.objects.filter(author_id=pk)
    most_viewed = articles.order_by('-views')[:1][0]  # Получаем самую просматриваемую
    recent_article = articles.order_by('-created_at')[:1][0] # Получаем последнию добавленную статью

    context = {
        'profile': profile,
        'title': f'Страница {request.user.username}',
        'most_viewed': most_viewed,
        'recent_article': recent_article,
        'articles': articles
    }

    return render(request, 'blog/profile.html', context)


def chg_profile_view(request):
    if request.user.is_authenticated:
        chg_account = ChgAccountForm(instance=request.user if request.user.is_authenticated else None)
        chg_profile = ProfileForm(instance=request.user.profile if request.user.is_authenticated else None)

        context = {
            'chg_form': chg_account,
            'title': 'Изменения данных',
            'chg_profile': chg_profile
        }

        messages.success(request, 'Данные изменены')
        return render(request, 'blog/change.html', context)


@login_required
def edit_account_view(request):
    if request.method == 'POST':
        form = ChgAccountForm(request.POST, instance=request.user)
        form2 = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid() and form2.is_valid():
            data = form.cleaned_data
            form2.save()
            user = User.objects.get(id=request.user.id)
            if user.check_password(data['old_password']):
                if data['old_password'] and data['new_password'] == data['confirm_password']:
                    user.set_password(data['new_password'])
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Пароль успешно изменён')
                    return redirect('profile', user.pk)
                else:
                    for field in form.errors:
                        messages.error(request, form.errors[field].as_text())
            else:
                for field in form.errors:
                    messages.error(request, form.errors[field].as_text())

            form.save()

        else:
            for field in form.errors:
                messages.error(request, form.errors[field].as_text())

        user = request.user
        return redirect('profile', user.pk)


