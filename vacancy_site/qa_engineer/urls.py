from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='qa-home'),
    path('geography', views.geography, name='geography'),
    path('demand', views.demand, name='demand'),
    path('recent-vacancies', views.recent_vacancies, name='recent-vacancies'),
    path('skills', views.skills, name='skills'),
]
