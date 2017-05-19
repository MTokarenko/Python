#!/usr/bin/env python3

import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.expected_conditions import \
    element_to_be_clickable as ECclick
from mydata import tezis


path_csv = 'C:/users.txt'
base_url = "http://localhost:28080/"

user_create_data = {'login': '[1]', 'psswd': '[2]', 'conf_psswd': '[3]',
                    'surname': '[4]', 'mail': '[8]'}
EC = webdriver.support.expected_conditions

subs_checker = input('Создать пользователей с замещением? [N] - Нет, Y - Да ')
if subs_checker in ['', 'N', 'n']:
    subs_checker = False
elif subs_checker in ['Y', 'y']:
    subs_checker = True
else:
    print('Введен неизвестный ключ - {}. Замещения не будут созданы'.format(subs_checker))
    subs = False


def get_users_from_csv(path_to_csv='C:/users.txt'):
    users_dic = dict()
    with open(path_to_csv) as f:
        for lino, line in enumerate(f):
            if lino != 0:
                line = line.split(';')
                test_list = []
                for index, word in enumerate(line):
                    test_list.append(word.strip())
                users_dic[test_list[0]] = test_list
    return users_dic

def drop_list(xpath_administration, xpath_users):
    click_but(xpath_administration)
    click_but(xpath_users)

def login():
    field_insert(tezis.LOGIN_FIELD, 'admin')
    field_insert(tezis.PSWD_FIELD, 'admin')
    click_but(tezis.ENTER_BTN)
    

def field_insert(field_xpath, field_value):
    field = wait.until(EC.presence_of_element_located((By.XPATH, field_xpath)))
    field.clear()
    click_but(field_xpath)
    field.send_keys(field_value)

def click_but(xpath):
    button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    button.click()
    
def user_create():
    create_but = '//div[@cuba-id="createPopupButton"]'
    create_new_but = '//div[@cuba-id="create"]'
    role_add_but = '//div[@cuba-id="rolesTableAddBtn"]'
    
    click_but(tezis.ADMINISTRATION_BTN)
    click_but(tezis.USERS_BTN)
    wait.until(EC.presence_of_element_located(
            (By.XPATH, create_but)))
    for role_index, user_data in enumerate(dict_csv.values()):
        drop_list(create_but, create_new_but)
        for num, field in enumerate(sorted(user_create_data.values())):
            field_xpath = tezis.NEW_USER_FIELD + field
            field_insert(field_xpath, user_data[num])
        (driver.find_element_by_xpath(tezis.NEW_USER_FIELD+'[9]')
         ).send_keys(Keys.SPACE) #flag sendWelcomeEmail
        (driver.find_element_by_xpath(tezis.NEW_USER_FIELD+'[16]')
         ).send_keys(Keys.SPACE) #flag changepswd
        click_but(tezis.GROUP_BTN)
        group = wait.until(EC.presence_of_element_located(
            (By.XPATH, tezis.LIMITED_ACCESS_BTN)))
        group.click()
        time.sleep(1)
        click_but(tezis.GROUP_CHOOSE_BTN)
        try:
            role_checker = user_data[5].split(',')
            for role in role_checker:
                click_but(role_add_but)
                time.sleep(1)
                role = '//div[contains(text(), "{0}")]'.format(role.strip())
                click_but(role)
                click_but('//div[@cuba-id="selectButton"]')
                time.sleep(1)
        except IndexError:
             pass
        click_but(tezis.OK_BTN)
        click_but('//div[@cuba-id="optionDialog_yes"]')
        time.sleep(1)
        click_but('//div[@cuba-id="windowCommit"]')
        time.sleep(1)

def create_users_substitution(names_list):
    user_field = '//div[@cuba-id="user"]/input'
    subs_field = '//div[@cuba-id="userSubstitution"]/input'
    ok_but = '//div[@cuba-id="windowCommit"]'
    user = "//table[@class = 'v-table-table']//tr/td[2]/div"
    subs_usr = "//table[@class = 'v-table-table']//tr/td[3]/div"
    adm = '//span[contains(text(), "admin")]'
    sub = '//span[contains(text(), "{0}")]'
    subs_create_but = '//div[@cuba-id="create"]'

    def get_list_from_table(table_xpath):
        lst_temp = driver.find_elements_by_xpath(table_xpath)
        time.sleep(1)
        lst = [x.text for x in lst_temp]
        return lst

    drop_list(tezis.REFERENCE_BTN, tezis.USERS_SUBS_BTN)
    time.sleep(1) #Переделать
    users = get_list_from_table(user)
    subs_users = get_list_from_table(subs_usr)
    tup = list(zip(users, subs_users))
    subs_users = [i[1] for i in tup if i[0] == 'Administrator']
    try:
        names_list.remove('Administrator')
    except:
        None
    names_set = set(names_list)
    subs_users_set = set(subs_users)
    final_set = names_set ^ subs_users_set
    for subs in final_set:
        click_but(subs_create_but)
        field_insert(user_field, 'admin')
        click_but(adm)
        field_insert(subs_field, subs)
        click_but(sub.format(subs))
        click_but(ok_but)


driver = webdriver.Chrome()
wait = webdriver.support.ui.WebDriverWait(driver, 10)
driver.maximize_window()
driver.get(base_url + "app/#!")
dict_csv = get_users_from_csv(path_csv)
login()
wait.until(EC.element_to_be_clickable((By.XPATH, tezis.TEZIS_BTN)))
user_create()
if subs_checker:
    names_list = [name for name in dict_csv.keys()]
    create_users_substitution(names_list)

driver.quit()
