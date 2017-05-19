#!/usr/bin/env python3

import time
import functools
import sys
import random
import selenium

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions \
    import element_to_be_clickable as ec_click
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from mydata import tezis
from mydata import database
from mydata.tezis import Process_BTNS


db_type = 'postgre'  # db_type can be 'postgre' or 'mssql'
db_name = 'gold'
rejected_list = ['Отменить процесс', 'Аннулировать', 'Аннулировано', 'Отменить согласование']
rejected_list_green = ['Доп.согласование']

db = database.Database(db_name, db_type)
EC = webdriver.support.expected_conditions
cur_state = 'ok'
user_btn_list = list()


try:
    if (sys.argv[1]).lower() == 'full':
        reject = True
    else:
        reject = False
except IndexError:
    reject = False
    

def drop_list(xpath_administration, xpath_users):
    driver.find_element_by_xpath(xpath_administration).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, xpath_users)))
    driver.find_element_by_xpath(xpath_users).click()


def cur_datetime():
    today = time.ctime()
    num = today.rfind(' ')
    today = today[0:num]
    locale = time.localtime()
    today = '{0}:{sec} {year}'.format(today, sec=locale.tm_sec, year=locale.tm_year)
    return today


def login():
    try:
        field_insert(tezis.LOGIN_FIELD, 'admin')
        field_insert(tezis.PSWD_FIELD, 'admin')
        click_but(tezis.ENTER_BTN)
        wait.until(EC.element_to_be_clickable((By.XPATH, tezis.TEZIS_BTN)))
        return True
    except selenium.common.exceptions.TimeoutException:
        print('Не удается найти элемент, убедитесь, что включена настройка cuba.testMode = true')
        return False


def field_insert(field_xpath, field_value):
    field = wait.until(EC.presence_of_element_located((By.XPATH, field_xpath)))
    field.clear()
    click_but(field_xpath)
    field.send_keys(field_value)


def click_but(xpath):
    button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    button.click()


def current_user_checker(user):
    text = './/td[contains(@class, "gwt-MenuItem")]//span'
    field = driver.find_element_by_xpath(tezis.CURRENT_USER_FIELD)
    cur_user = field.get_attribute("value")
    user_new = str()
    for ch in cur_user:
        if ch == ' ':
            break
        user_new += ch
    if user_new != user:
        field.clear()
        field.send_keys(user)
        wait.until(EC.presence_of_element_located((By.XPATH, text)))
        click_but('.//td[contains(@class, "gwt-MenuItem")]')
        wait.until(EC.element_to_be_clickable((By.XPATH,
                    './/div[contains(@id, "optionDialog_changeSubstUserAction")]')))
        click_but('.//div[contains(@id, "optionDialog_changeSubstUserAction")]')
        wait.until(EC.element_to_be_clickable((By.XPATH, tezis.TEZIS_BTN)))
        driver.get(link)


def get_assignment_id():
    try:
        elem = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH,
                            '//div[@cuba-id="resolutionsTable"]/div[2]//table//div')))
        action = ActionChains(driver)
        action.context_click(elem).perform()
        click_but('//div[@cuba-id="showSystemInfo"]')
        elem = wait.until(EC.presence_of_element_located((By.XPATH, tezis.ASSIGNMENT_ID)))
        assigned_id = elem.text
        click_but('.//div[@aria-label="close button"]')
        return assigned_id
    except TimeoutException:
        return False


def proc_action(button, text, checker='Ok'):
    if checker == 'Ok':
        click_but(tezis.SUCCESS_BTN_FORM.format(button))
    else:
        click_but(tezis.FAILURE_BTN_FORM.format(button))
    field_insert(Process_BTNS.COMMENT_AREA, text)
    click_but(Process_BTNS.WINDOW_COMMIT_BTN)
    driver.get(link)
    time.sleep(1)
    wait.until(EC.element_to_be_clickable((By.XPATH, tezis.SAVE_BTN)))


def counter(label):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args):
            if label and args[1] != 'Improvement':
                user = args[0]
                state_loc = args[1]
                if (user, state_loc) in func.__dict__:
                    func.__dict__[(user, state_loc)] = 1
                else:
                    func.__dict__[(user, state_loc)] = 0
                result = func(*args, checker=func.__dict__[(user, state_loc)])
                return result
            else:
                result = func(*args, checker=True)
                return result
        return wrapper
    return deco


def get_buttons_dict(user):
    buttons_dict = dict()
    btn_list_success = driver.find_elements_by_xpath(tezis.SUCCESS_BTN)
    btn_text = [btn.text for btn in btn_list_success]
    buttons_dict[user, 'success'] = btn_text
    btn_list_failure = driver.find_elements_by_xpath(tezis.FAILURE_BTN)
    btn_text = [btn.text for btn in btn_list_failure]
    buttons_dict[user, 'failure'] = btn_text
    return buttons_dict


def common_process(user, state):
    global user_btn_list
    if state != state_for_end:
        current_user_checker(user)
        wait.until(EC.element_to_be_clickable((By.XPATH, tezis.SAVE_BTN)))
        buttons_dict = get_buttons_dict(user)
        if reject:
            for tabu_state in rejected_list:
                if tabu_state in buttons_dict[user, 'failure']:
                    buttons_dict[user, 'failure'].remove(tabu_state)
            while len(buttons_dict[user, 'failure']) != 0:
                if (user, state, buttons_dict[user, 'failure'][0]) in user_btn_list:
                    buttons_dict[user, 'failure'].pop(0)
                elif len(buttons_dict[user, 'failure']) == 0:
                    for tabu_state in rejected_list_green:
                        if tabu_state in buttons_dict[user, 'success']:
                            buttons_dict[user, 'success'].remove(tabu_state)
                    proc_action(buttons_dict[user, 'success'][random.randint
                    (0, (len(buttons_dict[user, 'success']) - 1))], 'Я, {0}, согласовываю '
                                'данный документ.\n{1}'.format(user, time.ctime()))
                    break
                else:
                    user_btn_list.append((user, state, buttons_dict[user, 'failure'][0]))
                    proc_action(buttons_dict[user, 'failure'][0], 'Я, {0}, отказываюсь согласовывать '
                                'данный документ.\n{1}'.format(user, time.ctime()), checker=False)
                    break
            if len(buttons_dict[user, 'failure']) == 0:
                for tabu_state in rejected_list_green:
                    if tabu_state in buttons_dict[user, 'success']:
                        buttons_dict[user, 'success'].remove(tabu_state)
                proc_action(buttons_dict[user, 'success'][random.randint
                (0, (len(buttons_dict[user, 'success']) - 1))], 'Я, {0}, согласовываю '
                                'данный документ.\n{1}'.format(user, time.ctime()))
        else:
            for tabu_state in rejected_list_green:
                if tabu_state in buttons_dict[user, 'success']:
                    buttons_dict[user, 'success'].remove(tabu_state)
            proc_action(buttons_dict[user, 'success'][random.randint
            (0, (len(buttons_dict[user, 'success']) - 1))], 'Я, {0}, согласовываю '
                                'данный документ.\n{1}'.format(user, time.ctime()))
    else:
        print('Процесс достиг этапа {}'.format(state_for_end))
        global cur_state
        cur_state = 'exit'
        driver.quit()


def main(process_data, var):
    global cur_state
    if type(process_data) == dict:
        for i in process_data.keys():
            key = i
        for users in process_data.values():
            if cur_state == 'ok':
                common_process(users[0], key)
            elif cur_state == 'exit':
                break
        checker = db.get_process_data(card_id)
        if cur_state == 'ok':
            main(checker, True)
    elif type(process_data) != dict and var is False:
        print(process_data)
    elif type(process_data) != dict and var is True:
        print('Выполнение процесса завершено')

link = input('Введите ссылку на карточку -> ')
chrome_options = Options()
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(chrome_options=chrome_options)
driver.maximize_window()
wait = WebDriverWait(driver, 10)
driver.get(link)
try:
    if login():
        assignment_id = get_assignment_id()
        if assignment_id:
            card_id = db.get_card_id_from_assignment_id(assignment_id)
            proc_states = db.get_proc_states(assignment_id)
            states_locale_dict = db.get_states_from_design(assignment_id)
            states_dict = dict()
            if states_locale_dict:
                counter = 0
                for state in proc_states:
                    if state in states_locale_dict.keys():
                        counter += 1
                        print('{0:>3} {1:43} {2:43}'.format(str(counter), states_locale_dict[state][0:40] + '...' if
                                len(states_locale_dict[state]) > 40 else states_locale_dict[state], state))
                        states_dict[str(counter)] = state
            else:
                for number, state in enumerate(proc_states, start=1):
                    print('{0:3} {1}'.format(number, state))
                    states_dict[str(number)] = state
            print()
            state_for_end = ''
            if not reject:
                while True:
                    states_num = input('Введите номер этапа либо его название(англ), на котором необходимо'
                                       ' остановиться.\nДля прохождения всего процесса нажмите Enter --> ')
                    if states_num == '':
                        state_for_end = ''
                        break
                    elif states_num in states_dict.keys():
                        state_for_end = states_dict[states_num]
                        break
                    elif states_num in states_dict.values():
                        state_for_end = states_num
                        break
                    else:
                        print('\nВведен некорректный номер этапа - {}\n'.format(states_num))
                print(state_for_end)
            assignment_data = db.get_process_data(card_id)
            main(assignment_data, False)
        else:
            print('По данной карточке не запущен процесс либо скрыт журнал действий')
        driver.quit()
    else:
        driver.quit()
except selenium.common.exceptions.WebDriverException as err:
    driver.quit()
    print('Oops! Something wrong!\n{}'.format(err))
except IndexError as err:
    driver.quit()
    print('Oops! Something wrong! {0}\nВозможно, неверно указана БД - {1}\n'.format(err, db_name))
