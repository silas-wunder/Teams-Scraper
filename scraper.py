from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from time import sleep
from datetime import date, datetime
import json


# Set chrome options and pull password
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")
options.add_argument("--log-level=3")

# Email and Password for logging in
with open("pword.txt", 'r') as fp:
    pword = fp.read()
with open("email.txt", 'r') as fp:
    emailA = fp.read()

# The target URL
with open("url.txt", 'r') as fp:
    url = fp.read()

# Launch the webpage in a driver
driver = webdriver.Chrome(options=options)
driver.get(url)

# Find email field and input email
while(True):
    try:
        email = driver.find_element_by_id("i0116")
        break
    except NoSuchElementException:
        sleep(5)
        continue
email.send_keys(emailA)

# Click the next button
while(True):
    try:
        driver.find_element_by_id("idSIButton9").click()
        break
    except StaleElementReferenceException:
        sleep(5)
        continue
    except ElementNotInteractableException:
        sleep(5)
        continue

# Find the password field and input password
while(True):
    try:
        password = driver.find_element_by_id("i0118")
        break
    except NoSuchElementException:
        sleep(5)
        continue
password.send_keys(pword)

# Click the submit button
while(True):
    try:
        driver.find_element_by_id("idSIButton9").click()
        break
    except StaleElementReferenceException:
        sleep(5)
        continue
    except ElementNotInteractableException:
        sleep(5)
        continue

# Click no on the "save info" prompt
while(True):
    try:
        driver.find_element_by_id("idBtn_Back").click()
        break
    except StaleElementReferenceException:
        sleep(5)
        continue
    except ElementNotInteractableException:
        sleep(5)
        continue

# Find the correct team
while(True):
    try:
        driver.find_element_by_xpath('//div[@data-tid="team-CompSci CS253 Spr21"]').click()
        break
    except NoSuchElementException:
        sleep(5)
        continue

# Find the correct channel
while(True):
    try:
        driver.find_element_by_xpath('//a[@data-tid="team-CompSci CS253 Spr21-channel-Lecture and Lab Videos"]').click()
        break
    except NoSuchElementException:
        sleep(5)
        continue

# Open the messages
while(True):
    try:
        driver.find_element_by_xpath('//a[@data-tid="messageBodyCollapsedString"]').click()
        break
    except NoSuchElementException:
        sleep(5)
        continue
    except ElementNotInteractableException:
        sleep(5)
        continue

with open("lastTime.txt", 'r') as fp:
    latest_msg = datetime.strptime(fp.read(), '%b %d, %Y %I:%M %p')

# Repeat expanding messages until all messages are visible
clickCount = 0
count = 0
while(True):
    # Once the loop runs 8 times, stop
    if clickCount >= 8:
        break
    if count % 10 == 0:
        try:
            didSomething = False
            for element in driver.find_elements_by_xpath('//div[@aria-hidden="true"]'):
                if element.text.find("replies") != -1:
                    didSomething = True
                    element.click()
            clickCount += 1
            if not didSomething:
                break
        except NoSuchElementException:
            continue
    sleep(1)
    print("Working " + ("·" * ((count%5) + 1)).ljust(13), end='\r')
    count += 1

# Grab the html version of the entire page
soup = BeautifulSoup(driver.page_source, 'html.parser')
names = soup.find_all('div', {"data-tid": "threadBodyDisplayName"})
times = soup.find_all('span', {"data-tid": "messageTimeStamp"})

latest_time = times[-1]['title']

messages_since_last_run = 0
for time in reversed(times):
    time_msg = datetime.strptime(time['title'], '%b %d, %Y %I:%M %p')
    if time_msg <= latest_msg:
        break
    messages_since_last_run += 1

with open("lastTime.txt", 'w') as fp:
    fp.write(latest_time)

names_fixed = {}

with open("Dictionary.json") as fp:
    names_fixed = json.load(fp)

# Grab the name of every user that has chatted

if messages_since_last_run != 0:
    for name in names[-messages_since_last_run:]:
        real_name = name.text
        real_name = real_name.strip()
        if real_name in names_fixed:
            names_fixed[real_name] += 1
        else:
            names_fixed[real_name] = 1

with open('Dictionary.json', 'w') as fp:
    json.dump(names_fixed, fp)

driver.quit()
print()
