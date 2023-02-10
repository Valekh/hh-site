<h1> Туториал как написать сайт с вакансиями, регистрацией и CRUD на Django </h1>

![image](https://user-images.githubusercontent.com/59338155/218063959-e9c242ce-8b10-4b99-9760-b64f91df1690.png)


<h2> Начало и установка </h2>

Устанавливаем фреймворк Django:
  
    pip install django
Создаём проект в Django (у меня name - vacancy_site):

    django-admin startproject <name>

Создаём первый и основной раздел сайта:

    python manage.py startapp <name>
В нашем случае, имя выбрано `qa_engineer`. В файл `settings.py` в список `INSTALLED_APPS =` добавляем класс из `qa_engineer/apps.py` - `'qa_engineer.apps.QaEngineerConfig'`

<h2> Регистрация и вход на сайт </h2> 

![image](https://user-images.githubusercontent.com/59338155/218064089-b1fb7f7a-cadd-49ec-a726-f84cf28bdb4f.png)

Создаём раздел, отвечающий за работу с пользователями:

    python manage.py startapp users
Также добавляем его в файл `setting.py` в список `INSTALLED_APPS =`, в этот раз `'users.apps.UsersConfig'`.
В `users/views.py` прописываем код для регистрации:

```def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            return redirect('qa-home')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})
```
Если пользователь отправил POST-запрос (т.е. ввёл данные), мы проверяем валидна ли форма (джанго проверяет, правильно ли введены данные, надёжный ли пароль). Если да - данные из формы сохраняются, создаётся новый пользователь, происходит перенаправление на главную страницу.

Теперь нужно определить классы `UserRegisterForm` и класс для логина. Мы не используем дефолтные от Джанго для соблюдения вёрстки.

Создаём файл `users/models.py`, прописываем:

```
class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username']

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        del self.fields['password2']

        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None

        self.fields['username'].label = ""
        self.fields['password1'].label = ""

        self.fields['username'].widget = TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваш логин'})
        self.fields['password1'].widget = PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ваш пароль'})
```
Удаляем подтверждение пароля (соответствие вёрстке), help_text, названия форм (label), определяем placeholder (текст внутри форм).

Прописываем такое же для формы логина, которое мы используем позже:
```
class UserLoginForm(AuthenticationForm):
    model = User

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

        self.fields['username'].label = ""
        self.fields['password'].label = ""

        self.fields['username'].widget = TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваш логин'})
        self.fields['password'].widget = PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ваш пароль'})
```
Чтобы юзер при нажатии на выход сразу выходил, а не попадал на страницу с просьбой подтверждения, пишем в `vacancy_site/settings.py`:

    LOGOUT_REDIRECT_URL = "/"


<h2> Основные urlpatterns </h2>

Вводим все импорты в `vacancy_site/urls.py`:

```
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from users import views as user_views
from users.forms import UserLoginForm

from django.conf import settings
from django.conf.urls.static import static
```

Прописываем все паттерны, по которому будет работать сайт:

```
urlpatterns = [
    path('admin/', admin.site.urls),
    path('summernote/', include('django_summernote.urls')),
    path('', include('qa_engineer.urls')),
    path('register/', user_views.register, name="register"),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html', authentication_form=UserLoginForm), name="login"),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name="logout"),
]
```
Метод path принимает два аргумента: название url, которое будет отображаться в адресной строке; ссылка на нужный код; аргумент name опционален - название для паттерна. К примеру, в разделе регистрация, мы видим, что редирект совершается по названию паттерна.
Все запросы первым делом у нас отправляются в qa_engineer, для этого мы используем include. Если там нет совпадений, Джанго возвращается проверять сюда.
URL `admin` - раздел администрирования, `summernote` - модуль с CRUD, которое мы установим позже, `register` и `login/logout` - работа с юзерами. Регистрация ссылается на
созданный нами метод, логин на стандартный от Django (но мы указали использовать нашу вёрстку и нашу созданную форму). `logout` перенаправляет на пустой шаблон, но
это для галочки, у нас он не используется.

<h2> Основной сайт - qa_engineer </h2>

Прописываем в файле `qa_engineer/urls.py` ссылки на наши методы, которые сейчас создадим:

```
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='qa-home'),
    path('geography', views.geography, name='geography'),
    path('demand', views.demand, name='demand'),
    path('recent-vacancies', views.recent_vacancies, name='recent-vacancies'),
    path('skills', views.skills, name='skills'),
]
```

Переходим в `qa_engineer` и прописываем методы для страниц:

```
from django.shortcuts import render
from vacancies.vacancies import get_yesterday_vacancies
from .models import Post


def get_context(name: str):
    content = \
        {'content': Post.objects.filter(title=name).first(),
         'title': name}
    return content


def home(request):
    content = get_context('Главная')
    return render(request, 'qa_engineer/index.html', content)
```
`get_context` нужен для удобства - мы получаем названия раздела и ищем в бд контент для его. Бд заполним потом. Остальные методы сделаны по аналогии с `home`, который получает
контент из бд и рендерит шаблон, куда вставляет контент.

<h3> Шаблоны </h3>
Вот так выглядят наши шаблоны:

```
{% extends "qa_engineer/base.html" %}
{% load static %}
{% block title %} {{ title }} {% endblock %}
{% block section1 %}
    {{ content.section1|safe }}
{% endblock %}
{% block content %}
    {{ content.content|safe }}
{% endblock %}
```
`extends` отсылается на базовый шаблон, в котором содержится все элементы, присутствующих на всех страницах сайта (таким образом, нам не приходится писать везде одно и
то же). В файле `base.html` есть блоки `block title`, `block section1` и `block content`, в эти блоки и вставляется содержимое блоков с теми же названиями здесь. Всё,
что заключено в `{{ }}` - контент, переданный сюда в методе.
Все шаблоны лежат в папке `qa_engineer/templates/qa_engineer`.

<h2> Получить и отобразить вакансии с hh.ru </h2>

![image](https://user-images.githubusercontent.com/59338155/218064521-2195b4bb-d7af-4496-a7f4-05d7419d746b.png)

<h3> Пишем скрипт </h3>

В той же папке проекта, где лежат `qa_engineer`, `users` и `manage.py`, создаём папку `vacancies`, в которой создаём файл `__init__.py`, сообщающий питону, что эту
папку следует использовать как модуль. Затем создаём файл `vacancies.py`, в котором пишем:

```
import requests
from bs4 import BeautifulSoup

from datetime import datetime, timedelta


def get_yesterday_vacancies():
    today = datetime.now()
    yesterday = today - timedelta(1)
    yesterday = yesterday.strftime('%Y-%m-%d')
    vacancies = requests.get("https://api.hh.ru/vacancies?text=qa&order_by=publication_time&search_field=name&"
                             "date_from=2023-01-01&date_to=" + yesterday)
    answer = vacancies.json()['items']

    result = []

    for i in answer[:10]:
        fields = {}

        vacancy = requests.get("https://api.hh.ru/vacancies/" + i['id'])
        vacancy = vacancy.json()

        soup = BeautifulSoup(vacancy['description'], features="html.parser")
        description = soup.get_text()

        date = datetime.strptime(vacancy['published_at'], "%Y-%m-%dT%H:%M:%S+0300")
        date = date.strftime("%d/%m/%Y, %H:%M")

        salary = vacancy['salary']
        if salary is not None:
            if salary['to'] is not None:
                salary = salary['to']
            else:
                salary = salary['from']

            slr = salary
            salary = str(slr) + " " + vacancy['salary']['currency']
        else:
            salary = ''

        skills = []
        for skill in vacancy['key_skills']:
            skills.append(skill['name'])
        skills = ", ".join(skills)

        fields.update({"name": vacancy['name'],
                       "key_skills": skills,
                       "employer_name": vacancy['employer']['name'],
                       "area": vacancy['area']['name'],
                       "link": vacancy['alternate_url'],
                       "date": date,
                       "description": description,
                       "salary": salary})
        result.append(fields)

    return result
 ```
 Сразу же прописываем `pip install bs4` для установки нужной библиотеки (она очищает текст от HTML-тегов, которые возвращает hh.ru). 
 Метод получает вчерашние вакансии, указывая в качестве даты вчерашний день (требование задания), и в цикле запрашивает подробную информацию по каждому из первых десяти.
 Полученные результаты приводит в нужный вид и возвращает.
 
 В файл `qa_engineer/views.py` добавляем метод, обращающийся к нашему скрипту:
 
 ```
 def recent_vacancies(request):
    vacancies = get_yesterday_vacancies()
    context = {
        'vacancies': vacancies
    }
    return render(request, "qa_engineer/recent-vacancies.html", context)
 ```
 
 В `qa_engineer/recent-vacancies.html` цикл, обрабатывающий полученные данные:
 
 ```
  {% for vacancy in vacancies %}
                    <div class="content-vacancy__item">
                        <h3 id="vacancyName">{{ vacancy.name }}</h3>
                        <p id="vacancyInfo">
                          {{ vacancy.description|safe|truncatewords:"20"|linebreaks }}
                          <a href="{{ vacancy.link }}" target="_blank">Подробнее</a>
                        </p>
                          <p id="vacancySkills">
                            Навыки:
                              {{ vacancy.key_skills }}
                          </p>
                          <p id="vacancyCompany"> {{ vacancy.employer_name }}</p>
                          <p id="vacancySalary">{% if vacancy.salary != "" %} Оклад: {{ vacancy.salary }} {% endif%}</p>
                          <p id="vacancyRegion"> {{ vacancy.area }} </p>
                          <p id="vacancyDate"> {{vacancy.date }}</p>
                    </div>
                {% endfor %}
```
Как можно заметить, цикл пропускает надпись "Оклад", если пункт "зарплата" пустой.
 
 <h2> Как же сделать CRUD? </h2>
 
 В файле `qa_engineer/models.py` (если нет - создать) создаём модель поста:
 
 ```
 from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=140)
    section1 = models.TextField()
    content = models.TextField()

    def __str__(self):
        return self.title
```
 
 Устанавливаем `summernote` по инструкции здесь: https://github.com/summernote/django-summernote
 
 Перед тем, как в `qa_engineer/admin.py` ставить `admin.site.register(Post, SomeModelAdmin)`, оставляем `admin.site.register(Post)`, в админской заполняем в БД
 посты без форматирования (копипаст нужных разделов из html), ставим `admin.site.register(Post, SomeModelAdmin)` и перезагружаем - summernote всё приведёт в нужный вид.
 Нужные картинки придётся проставить вручную.
