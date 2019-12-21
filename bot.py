from random import randint
from time import sleep

import requests
import telebot
from telebot import types

from project import Project

from config import BOT_TOKEN, TOKEN, words, except_words, my_tg_id

url = 'https://api.freelancehunt.com/v2/projects'
params = {'filter[skill_id]': 180}
headers = {'Authorization': f'Bearer {TOKEN}'}


bot = telebot.TeleBot(BOT_TOKEN)
last_update_id = 0


def link_markup(url):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Перейти', url=url))
    return markup


@bot.message_handler(commands=['start'])
def start_cmd(msg: types.Message):
    projects = find_projects()
    text = ''
    for project in projects:
        text += f'{project["name"]}\n' \
               f'[ПЕРЕЙТИ]({project["link"]})\n\n'
    if text:
        bot.send_message(msg.from_user.id, text, disable_web_page_preview=True, parse_mode='Markdown')
    else:
        bot.send_message(msg.from_user.id, 'Новых проектов нет 😔')


def check_words(name: str) -> bool:
    result = False
    for word in words:
        if word.lower() in name:
            result = True
    for except_word in except_words:
        if except_word in name:
            result = False
    return result


def save_history(id, name):
    with open('history', mode='a', encoding='utf-8') as file:
        file.write(f'{id}:{name}\n')


def check_history(id) -> bool:
    result = False
    try:
        with open('history', mode='r', encoding='utf-8') as file:
            for line in file:
                if str(id) == line.split(':')[0]:
                    result = True
    except FileNotFoundError:
        result = False
    return result


def find_projects():
    global params
    pages = 2
    page = 1
    result = []
    while page <= pages:
        response = requests.get(url, params=params, headers=headers)
        json_response = response.json()
        projects = json_response['data']
        for project in projects:
            id = project['id']
            name = project['attributes']['name']
            link = project['links']['self']['web']
            status = project['attributes']['status']['id']
            try:
                budget_amount = project['attributes']['budget']['amount']
                budget_currency = project['attributes']['budget']['currency']
            except KeyError:
                budget_amount = None
                budget_currency = None
            bid_count = project['attributes']['bid_count']
            if check_words(name) and not check_history(id):
                result.append(Project(name, link, status, budget_amount, budget_currency, bid_count))
                save_history(id, name)
        page += 1
        params = {'page[number]': page, 'skill_id': 180}
    return result


if __name__ == '__main__':
    while True:
        projects = find_projects()
        print(f'RESULT: {len(projects)} new projects.')
        for project in projects:
            text = f'{project.name}\n' \
                   f'Ставок: {project.bid_count}\n'
            if project.budget_amount:
                text += f'Бюджет: {project.budget_amount} '
                if project.budget_currency == 'UAH':
                    text += '₴'
                else:
                    text += '₽'
            bot.send_message(my_tg_id, text,
                             disable_web_page_preview=True,
                             parse_mode='Markdown',
                             reply_markup=link_markup(project.link))
        print('Bot watch new messages')
        updates = bot.get_updates(offset=(bot.last_update_id + 1), timeout=0)
        bot.process_new_updates(updates)
        print('Bot stop watch new messages')
        sleep_time = randint(10, 30)
        print(f'SLEEP {sleep_time} sec.'.center(70, '-'))
        sleep(sleep_time)
