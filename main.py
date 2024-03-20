from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options
import time

# Login and initial setup
login_url = "https://www.afbostader.se/"
booking_url = "https://www.afbostader.se/dina/sidor/boka-bastu/"
session = requests.Session()
response = session.get(login_url)
soup = BeautifulSoup(response.content, 'html.parser')
viewstate = soup.find('input', {'id': '__VIEWSTATE'}).get('value', '')
eventvalidation = soup.find('input', {'id': '__EVENTVALIDATION'}).get('value', '')

payload = {
    "ctl00$ctl25$LoginControl$UserName": "mans.holmgren@gmail.com",
    "ctl00$ctl25$LoginControl$Password": "Jerkman132",
    "__VIEWSTATE": viewstate,
    "__EVENTVALIDATION": eventvalidation,
    "ctl00$ctl25$LoginControl$btnLogIn": "Logga in"
}
session.post(login_url, data=payload)

options = Options()
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)
driver.get(login_url)

for cookie in session.cookies:
    driver.add_cookie({'name': cookie.name, 'value': cookie.value, 'domain': cookie.domain, 'path': '/', 'secure': cookie.secure})
driver.get(booking_url)

def find_sundays():
    today = datetime.today()
    days_until_next_sunday = 6 - today.weekday() + 1
    if days_until_next_sunday > 7:
        days_until_next_sunday -= 7

    next_sunday = today + timedelta(days=days_until_next_sunday)
    sunday_after_next = next_sunday + timedelta(days=7)
    return next_sunday, sunday_after_next

def select_date(driver, date):
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "datepicker"))).click()
    
    # Logic to navigate to the correct month, if necessary, goes here
    
    first_day_of_month = date.replace(day=1)
    offset = (first_day_of_month.weekday() + 1) % 7
    row = ((date.day + offset - 1) // 7) + 1
    
    day_xpath = f"//*[@id='datepicker']/div/div/table/tbody/tr[{row}]/td[7]"
    print(f"Selecting date using XPath: {day_xpath}")
    day_to_select = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, day_xpath)))
    day_to_select.click()

def try_booking_for_date(driver, date):
    formatted_date = date.strftime("%Y-%m-%d")
    xpath = f"//a[@class='btn-default'][@data-date='{formatted_date}'][@data-timefrom='20:00'][@data-timeto='23:00']"
    try:
        booking_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        booking_button.click()
        return True
    except TimeoutException:
        return False

def continuously_monitor_and_book(driver):
    next_sunday, sunday_after_next = find_sundays()

    while True:
        for target_date in [next_sunday, sunday_after_next]:
            print(f"Checking availability for {target_date.strftime('%Y-%m-%d')} at 20:00-23:00...")
            select_date(driver, target_date)
            if try_booking_for_date(driver, target_date):
                print(f"Successfully booked for {target_date.strftime('%Y-%m-%d')} at 20:00-23:00!")
                return
            else:
                print(f"No available slot for {target_date.strftime('%Y-%m-%d')} at 20:00-23:00.")

        # Wait before the next check to avoid hammering the server with requests
        print("No slots available for the next two Sundays. Will check again in 60 seconds.")
        time.sleep(10)  # Sleep for 60 seconds before checking again

continuously_monitor_and_book(driver)
