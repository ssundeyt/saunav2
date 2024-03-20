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
#driver = webdriver.Firefox(options=options)
driver = webdriver.Firefox()
driver.get(login_url)

for cookie in session.cookies:
    driver.add_cookie({'name': cookie.name, 'value': cookie.value, 'domain': cookie.domain, 'path': '/', 'secure': cookie.secure})
driver.get(booking_url)

def find_sundays():
    today = datetime.today()
    days_until_next_sunday = 6 - today.weekday()
    if days_until_next_sunday < 0:  # Sunday is 6, so for Sunday this would be -1, ensuring we look to the next week
        days_until_next_sunday += 7

    next_sunday = today + timedelta(days=days_until_next_sunday)
    sunday_after_next = next_sunday + timedelta(days=7)
    return next_sunday, sunday_after_next

def select_date(driver, date):
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "datepicker"))).click()
    
    current_month = datetime.now().month
    target_month = date.month
    month_diff = (target_month - current_month) % 12

    if month_diff != 0:
        for _ in range(month_diff):
            next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'next')]")))
            next_button.click()
            time.sleep(1)

    first_day_of_target_month = date.replace(day=1)
    first_sunday_of_month = first_day_of_target_month + timedelta(days=(6-first_day_of_target_month.weekday()) % 7)
    weeks_between = (date - first_sunday_of_month).days // 7
    row = weeks_between + 1

    day_xpath = f"//*[@id='datepicker']/div/div/table/tbody/tr[{row}]/td[7]"
    day_to_select = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, day_xpath)))
    day_to_select.click()

def try_booking_for_date(driver, date):
    formatted_date = date.strftime("%Y-%m-%d")
    # Use a more specific XPath that targets the 20:00-23:00 booking button directly
    xpath = f"//*[@id='content']/div[4]/section/div/div/div[3]/div/div[1]/div/div/div/div[5]/div/div[2]/div/div/a[@data-date='{formatted_date}']"

    try:
        print(f"Trying to book for {formatted_date} at 20:00-23:00...")
        booking_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        booking_button.click()
        print(f"Clicked booking button for {formatted_date} at 20:00-23:00.")
        
        # Optional: Add a verification step here to check if the booking was successful.
        # This could involve checking for a confirmation message or dialog.

        return True
    except TimeoutException:
        print(f"Booking button not found or not clickable for {formatted_date} at 20:00-23:00.")
        return False

def continuously_monitor_and_book(driver):
    next_sunday, sunday_after_next = find_sundays()

    while True:
        for target_date in [next_sunday, sunday_after_next]:
            print(f"Refreshing the page before checking availability...")
            driver.refresh()  # Refresh the page

            # Wait for a moment to let the page fully load after refresh
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "content")))

            print(f"Checking availability for {target_date.strftime('%Y-%m-%d')} at 20:00-23:00...")
            select_date(driver, target_date)
            if try_booking_for_date(driver, target_date):
                print(f"Successfully booked for {target_date.strftime('%Y-%m-%d')} at 20:00-23:00!")
                return
            else:
                print(f"No available slot for {target_date.strftime('%Y-%m-%d')} at 20:00-23:00...")

        # Wait before the next check to avoid hammering the server with requests
        time.sleep(10)  # Adjust the sleep time as necessary


continuously_monitor_and_book(driver)
