import discord
from discord.ext import commands
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import time
import os

chrome_options = Options()
chrome_options.add_argument("--headless")
intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False
intents.messages = True
intents.guilds = True
intents.members = True


Members = {
    "member1": {"username": "211777", "password": "Y4354543", "id":"324242342424556"},
  
}

ErrorList = []
PassedList = []
AllList = []
link = "https://e-learning.msa.edu.eg/login/index.php"

drivers = {}

for member, credentials in Members.items():
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(link)
        try:
            continue_button = driver.find_element("xpath", "//input[@value='Continue']")
            continue_button.click()
        except NoSuchElementException:
            print("Continue Exception Handled")

        username = credentials["username"]
        password = credentials["password"]
        username_field = driver.find_element("name", 'username')
        password_field = driver.find_element("name", 'password')
        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button = driver.find_element("xpath", "//input[@value='Log in']")
        login_button.click()

        drivers[member] = driver

        time.sleep(1)
        if not driver.find_elements("id", "loginerrormessage"):
            PassedList.append(member)
        else:
            ErrorList.append(member)
            # driver.close()
    except:
        pass

print("Pass", PassedList)
print("Error", ErrorList)

bot = commands.Bot(command_prefix="!", intents=intents) 

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    while True:

        def scrape_courses(driver):
            try:
                course_elements = driver.find_elements("xpath", "//a[starts-with(@id, 'label_3_')]")
                courses = {}
                for element in course_elements:
                    course_id = element.get_attribute("id")
                    course_name = element.text
                    course_link = element.get_attribute("href")
                    courses[course_id] = {"name": course_name, "link": course_link}
                return courses
            except:
                pass

        def scrape_course_contents(driver, course_link):
            try: 
                driver.get(course_link)
                content_elements = driver.find_elements("class name", "instancename")
                contents = []
                for element in content_elements:
                    content_name = element.text
                    contents.append(content_name)
                return contents
            except:
                pass   

        def save_contents_to_file(member, course_name, contents):
            directory = f"Archives/{member}"
            if not os.path.exists(directory):
                os.makedirs(directory)

            filename = f"{directory}/{member}_{course_name}.txt"
            with open(filename, "w") as file:
                for content in contents:
                    file.write(content + "\n")

        def check_for_new_contents(member, course_name, contents):
            try:
                directory = f"Archives/{member}"
                filename = f"{directory}/{member}_{course_name}.txt"
                if not os.path.exists(filename):
                    save_contents_to_file(member, course_name, contents)
                    return contents

                with open(filename, "r") as file:
                    stored_contents = [line.strip() for line in file]

                new_contents = [content for content in contents if content not in stored_contents]

                if new_contents:
                    save_contents_to_file(member, course_name, contents)
                    return new_contents

                return []
            except:
                pass
            
        for member, driver in drivers.items():
            try:
                if member in PassedList:
                    courses = scrape_courses(driver)
                    new_assignments = []

                    for course_id, course_info in courses.items():
                        course_name = course_info["name"]
                        course_link = course_info["link"]

                        contents = scrape_course_contents(driver, course_link)
                        new_contents = check_for_new_contents(member, course_name, contents)

                        if new_contents:
                            new_assignments.extend([f"{course_name}: {content}" for content in new_contents])

                    if new_assignments:
                        # #for DMs
                        # user_id = Members[member]["id"]
                        # user = await bot.fetch_user(user_id)
                        # dm_channel = await user.create_dm()
                        # message = f"New addition in your courses:\n" + "\n".join(new_assignments)
                        # await dm_channel.send(message)
                        #For channel
                        channel = bot.get_channel(1080632622188875900)
                        await channel.send(f"New course additions for {member}:\n {new_assignments}")
                        
                        print(f"New course additions for {member}: {new_assignments}")
                        
                    print("DONE: ",member)
            except:
                print("Error In Parse")


bot.run("token")
