from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import element_to_be_clickable as ECclick

EC = webdriver.support.expected_conditions
driver = webdriver.Chrome
wait = webdriver.support.ui.WebDriverWait(driver, 10)

class Box():
    ADMINISTRATION_BTN = '//span[@cuba-id="administration"]'
    USERS_BTN = '//span[@cuba-id="sec$User.browse"]'
    NEW_USER_FIELD = '//div[contains(text(), "Логин")]/following::input'
    GROUP_BTN = '//div[contains(text(), "Группа")]/following::div[@role = "button"][1]'
    LIMITED_ACCESS_BTN = '//span[contains(text(), "Ограниченный доступ")]'
    GROUP_CHOOSE_BTN = '//div[contains(text(), "Группы доступа")]/following::div[@role = "button"][1]'
    LOGIN_FIELD = '//input[@cuba-id="loginField"]'
    PSWD_FIELD = '//input[@cuba-id="passwordField"]'
    TEZIS_BTN = '//div[@cuba-id="logoImage"]'
    ENTER_BTN = '//div[@cuba-id="loginSubmitButton"]'
    OK_BTN = '//div[@cuba-id="windowCommit"]'
    REFERENCE_BTN = '//span[@cuba-id="reference"]'
    USERS_SUBS_BTN = '//span[@cuba-id="df$UserSubstitution.browse"]'
