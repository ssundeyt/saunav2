from optparse import Option
import os
import time
import getpass
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from selenium.webdriver.firefox.options import Options

def login_and_get_preferences(driver, login_url, booking_url):
    while True:
        driver.get(login_url)
        
        email_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="UserName"]'))) #xpath
        password_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="Password"]'))) #xpath
        login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl29_LoginControl_LoginButton"]'))) #xpath. Vi skiter i "kom ihåg" knappen
        
        email = input("email till afb: ")
        password = getpass.getpass("password till afb: ")

        email_input.clear() #ta bort tidigare autofyll värden
        email_input.send_keys(email)

        password_input.clear() #ta bort tidigare autofyll värden
        password_input.send_keys(password)

        login_button.click()

        time.sleep(5)
        if driver.current_url == booking_url:
            print("inloggning lyckades!")
            time.sleep(1)
            break
        else:
            print("Inloggning misslyckades, testa igen.\n")

    day_of_week, selected_time_slot = get_user_preferences()
    return day_of_week, selected_time_slot

def get_user_preferences(): #listar datum och tider samt tar upp 1-7 istället för pythons 0-6 för dagar...
    print("\nMata in en dag (1=Mndag, 7=Sndag):")
    day_of_week = int(input("Nummer dag: ")) % 7
    print("\nMata in en tid:")
    time_slots = ["08.00-11.00", "11.00-14.00", "14.00-17.00", "17.00-20.00", "20.00-23.00"]
    for i, time_slot in enumerate(time_slots, start=1):
        print(f"{i}. {time_slot}")
    time_choice = int(input("Nummer tid: "))
    selected_time_slot = time_slots[time_choice - 1] #... här
    return day_of_week, selected_time_slot

options = Options()
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)
login_url = "https://www.afbostader.se/?ReturnUrl=%2fdina%2fsidor%2fboka-bastu%2f" #denna url skickar användaren direkt till inloggningsformuläret. Det är latare än att få selenium att öppna fliken själv :)
booking_url = "https://www.afbostader.se/dina/sidor/boka-bastu/"
chosen_day_of_week, chosen_time_slot = login_and_get_preferences(driver, login_url, booking_url)

def select_date(driver, date):
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "datepicker"))).click()
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='datepicker-days']")))
    day_xpath = f"//div[@class='datepicker-days']//td[not(contains(@class, 'old')) and not(contains(@class, 'new')) and text()='{date.day}']"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, day_xpath))).click()
    pass

def find_next_day_of_week(day_of_week):
    today = datetime.today()
    days_ahead = (day_of_week - today.weekday() - 1) % 7 + 1
    return today + timedelta(days=days_ahead)

def try_booking_for_date(driver, date, time_slot):
    # mappning av tider till respektive xpath
    time_slot_xpath_mapping = {
        "08.00-11.00": "1",
        "11.00-14.00": "2",
        "14.00-17.00": "3",
        "17.00-20.00": "4",
        "20.00-23.00": "5"
    }

    formatted_date = date.strftime("%Y-%m-%d")
    xpath_index = time_slot_xpath_mapping.get(time_slot)
    
    if xpath_index:
        xpath = f"//*[@id='content']/div[4]/section/div/div/div[3]/div/div[1]/div/div/div/div[{xpath_index}]/div/div[2]/div/div/a[@data-date='{formatted_date}']"
        try:
            booking_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            booking_button.click()
            return True
        except TimeoutException:
            return False
    else:
        print(f"tiden {time_slot} finns inte som alternativ hos afb.")
        return False

def continuously_monitor_and_book(driver, day_of_week, time_slot): #loopen för att checka efter avbokningar
    this_week_date = find_next_day_of_week(day_of_week)
    next_week_date = this_week_date + timedelta(days=7)
    
    while True:
        for target_date in [this_week_date, next_week_date]:
            print(f"uppdaterar sidan...")
            driver.refresh()
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "content")))
            select_date(driver, target_date)
            if try_booking_for_date(driver, target_date, time_slot):
                print(f"Bokade bastun {target_date.strftime('%Y-%m-%d')} vid {time_slot}!")
                return
            else:
                print(f"fullbokat {target_date.strftime('%Y-%m-%d')} vid {time_slot} ")
            time.sleep(10)

continuously_monitor_and_book(driver, chosen_day_of_week - 1, chosen_time_slot)
