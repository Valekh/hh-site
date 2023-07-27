<h1> Tutorial on How to Build a Website with Job Vacancies, Registration, and CRUD in Django </h1>

![image](https://user-images.githubusercontent.com/59338155/218063959-e9c242ce-8b10-4b99-9760-b64f91df1690.png)

<h2> Getting Started and Installation </h2>

Install the Django framework:

```
pip install django
```

Create a Django project (let's call it "vacancy_site"):

```
django-admin startproject <name>
```

Create the main app for the website:

```
python manage.py startapp <name>
```

In this case, we've named the app "qa_engineer". In the file `settings.py`, add the app to the `INSTALLED_APPS` list:

```python
INSTALLED_APPS = [
    # ... other installed apps ...
    'qa_engineer.apps.QaEngineerConfig',
    # ... other installed apps ...
]
```

<h2> Registration and Login </h2> 

![image](https://user-images.githubusercontent.com/59338155/218064089-b1fb7f7a-cadd-49ec-a726-f84cf28bdb4f.png)

Create a section for managing users:

```
python manage.py startapp users
```

Add this app to the `INSTALLED_APPS` list in `settings.py`:

```python
INSTALLED_APPS = [
    # ... other installed apps ...
    'users.apps.UsersConfig',
    # ... other installed apps ...
]
```

In `users/views.py`, implement the registration code:

```python
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            return redirect('qa-home')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})
```

Now, define the classes `UserRegisterForm` and the login class. We are using our own forms for custom styling.

In `users/models.py`, create the `UserRegisterForm`:

```python
from django import forms
from django.contrib.auth.models import User

class UserRegisterForm(forms.ModelForm):
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

        self.fields['username'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your username'})
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Your password'})
```

Implement the same for the login form:

```python
from django.contrib.auth.forms import AuthenticationForm

class UserLoginForm(AuthenticationForm):
    model = User

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

        self.fields['username'].label = ""
        self.fields['password'].label = ""

        self.fields['username'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your username'})
        self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Your password'})
```

To make the user log out immediately without confirmation, add the following line to `vacancy_site/settings.py`:

```python
LOGOUT_REDIRECT_URL = "/"
```

<h2> Main Website - qa_engineer </h2>

In `qa_engineer/urls.py`, define the URL patterns for the main pages:

```python
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

Implement the views for these pages in `qa_engineer/views.py`:

```python
from django.shortcuts import render
from vacancies.vacancies import get_yesterday_vacancies
from .models import Post

def get_context(name: str):
    content = \
        {'content': Post.objects.filter(title=name).first(),
         'title': name}
    return content

def home(request):
    content = get_context('Home')
    return render(request, 'qa_engineer/index.html', content)
``

`

Implement similar views for the other pages (`geography`, `demand`, `skills`).

<h3> Templates </h3>
Templates in Django extend a base template that contains common elements across all pages. Create a `qa_engineer/base.html` template with the following structure:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}{% endblock %}</title>
    <!-- Other common head elements -->
</head>
<body>
    <!-- Common body elements -->
    <div class="section1">
        {% block section1 %}{% endblock %}
    </div>
    <div class="content">
        {% block content %}{% endblock %}
    </div>
    <!-- Other common body elements -->
</body>
</html>
```

In other templates (e.g., `qa_engineer/index.html`), you can extend the base template and fill in the blocks:

```html
{% extends "qa_engineer/base.html" %}
{% load static %}
{% block title %}{{ title }}{% endblock %}
{% block section1 %}
    {{ content.section1|safe }}
{% endblock %}
{% block content %}
    {{ content.content|safe }}
{% endblock %}
```

<h2> Fetch and Display Vacancies from hh.ru </h2>

![image](https://user-images.githubusercontent.com/59338155/218064521-2195b4bb-d7af-4496-a7f4-05d7419d746b.png)

<h3> Write a Script </h3>

In the same project folder as `qa_engineer`, `users`, and `manage.py`, create a new folder named `vacancies`. Inside the `vacancies` folder, create an empty file named `__init__.py`, which tells Python to treat this folder as a module. Then, create a file named `vacancies.py`, and write the following code:

```python
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

Note: Install `beautifulsoup4` and `requests` using `pip install beautifulsoup4 requests` if you haven't already.

The `get_yesterday_vacancies()` function fetches yesterday's vacancies using the HH.ru API. It processes the data and returns a list of dictionaries with the relevant information.

In `qa_engineer/views.py`, add a method to call our script:

```python
def recent_vacancies(request):
    vacancies = get_yesterday_vacancies()
    context = {
        'vacancies': vacancies
    }
    return render(request, "qa_engineer/recent-vacancies.html", context)
```

Create a template for displaying the vacancies, `qa_engineer/recent-vacancies.html`:

```html
{% for vacancy in vacancies %}
<div class="content-vacancy__item">
    <h3 id="vacancyName">{{ vacancy.name }}</h3>
    <p id="vacancyInfo">
        {{ vacancy.description|safe|truncatewords:"20"|linebreaks }}
        <a href="{{ vacancy.link }}" target="_blank">Learn more</a>
    </p>
    <p id="vacancySkills">
        Skills: {{ vacancy.key_skills }}
    </p>
    <p id="vacancyCompany">{{ vacancy.employer_name }}</p>
    <p id="vacancySalary">{% if vacancy.salary != "" %} Salary: {{ vacancy.salary }} {% endif%}</p>
    <p id="vacancyRegion">{{ vacancy

.area }}</p>
    <p id="vacancyDate">{{ vacancy.date }}</p>
</div>
{% endfor %}
```

In the above template, we use a loop to iterate through the vacancies list and display the relevant information for each vacancy. The `truncatewords` filter is used to limit the length of the description, and the `linebreaks` filter converts line breaks into HTML line breaks.

<h2> Implementing CRUD </h2>

In `qa_engineer/models.py` (if not already created), define a model for the posts:

```python
from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=140)
    section1 = models.TextField()
    content = models.TextField()

    def __str__(self):
        return self.title
```

Install `django-summernote` as per the instructions provided here: https://github.com/summernote/django-summernote

Before registering the model in `qa_engineer/admin.py`, register it initially without using `SomeModelAdmin`. Fill the database with posts without formatting (copy and paste the required sections from the HTML). After that, use `admin.site.register(Post, SomeModelAdmin)` and reload the page to let `summernote` format the content. You may need to set the required images manually.
