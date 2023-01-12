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

# Название вакансии;
# Описание вакансии;
# Навыки (в строку, через запятую)
# Компания
# Оклад
# Название региона
# Дату публикации вакансии.
