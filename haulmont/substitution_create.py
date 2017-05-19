#!/usr/bin/env python3

import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions \
    import element_to_be_clickable as ec_click
from selenium.webdriver.support.ui import WebDriverWait
from data import Box


base_url = "http://localhost:48080/app/#!"
EC = webdriver.support.expected_conditions
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

driver.maximize_window()
driver.get(base_url)


def drop_list(xpath_administration, xpath_users):
    driver.find_element_by_xpath(xpath_administration).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, xpath_users)))
    driver.find_element_by_xpath(xpath_users).click()


def login():
    field_insert(Box.LOGIN_FIELD, 'admin')
    field_insert(Box.PSWD_FIELD, 'admin')
    click_but(Box.ENTER_BTN)
    wait.until(EC.element_to_be_clickable((By.XPATH, Box.TEZIS_BTN)))


def field_insert(field_xpath, field_value):
    field = wait.until(EC.presence_of_element_located((By.XPATH, field_xpath)))
    field.clear()
    click_but(field_xpath)
    field.send_keys(field_value)


def click_but(xpath):
    button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    button.click()


def get_list_from_table(table_xpath):
    lst_temp = driver.find_elements_by_xpath(table_xpath)
    time.sleep(1)
    lst = [x.text for x in lst_temp]
    return lst


def get_all_users_list():
    name = "//table[@class = 'v-table-table']//tr/td[3]/div"
    click_but(Box.ADMINISTRATION_BTN)
    click_but(Box.USERS_BTN)
    time.sleep(2)
    wait.until(EC.presence_of_all_elements_located((By.XPATH, name)))
    return get_list_from_table(name)


def create_users_substitution():
    user_field = '//div[@cuba-id="user"]/input'
    subs_field = '//div[@cuba-id="userSubstitution"]/input'
    ok_but = '//div[@cuba-id="windowCommit"]'
    user = "//table[@class = 'v-table-table']//tr/td[2]/div"
    subs_usr = "//table[@class = 'v-table-table']//tr/td[3]/div"
    adm = '//span[contains(text(), "Administrator")]'
    sub = '//span[contains(text(), "{0}")]'

    drop_list(Box.REFERENCE_BTN, Box.USERS_SUBS_BTN)
    time.sleep(1)  # Переделать
    users = get_list_from_table(user)
    subs_users = get_list_from_table(subs_usr)
    tup = list(zip(users, subs_users))
    subs_users = [i[1] for i in tup if i[0] == 'Administrator']
    subs_create_but = '//div[@cuba-id="create"]'
    names.remove('Administrator')
    names_set = set(names)
    subs_users_set = set(subs_users)
    final_set = names_set ^ subs_users_set
    for subs in final_set:
        click_but(subs_create_but)
        field_insert(user_field, 'admin')
        click_but(adm)
        field_insert(subs_field, subs)
        click_but(sub.format(subs))
        click_but(ok_but)
    print('The End!')
    driver.quit()

login()
names = get_all_users_list()
create_users_substitution()
