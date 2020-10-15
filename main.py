from configparser import ConfigParser
import os
import getpass
import mysql.connector
import random
import string
from twilio.rest import Client

################## Tempomary Variables ##################
logged = False
logged_user = ""


################## Tempomary Variables ##################

class twilioAPI:
    def sendMessage(phone, body):
        config = ConfigParser()
        config.read("config.ini")
        config_variables = config["TwilioAPI"]
        token = str(config_variables["token"])
        account = str(config_variables["account"])
        phoneAPI = str(config_variables["ApiPhone"])

        client = Client(account, token)
        client.api.account.messages.create(
            to=f"{phone}",
            from_=f"{phoneAPI}",
            body=f"\n{body}")


class loginSystem():
    def login():
        global logged, logged_user
        config = ConfigParser()
        config.read("config.ini")
        config_variables = config["Settings"]
        config_variablesdb = config["MySQL"]
        name = str(config_variables["name"])
        x = len(name) + 2
        mydb = mysql.connector.connect(
            host=config_variablesdb["host"],
            user=config_variablesdb["user"],
            password=config_variablesdb["password"],
            port=config_variablesdb["port"],
            database=config_variablesdb["database"]
        )

        print("#" * (20 + x))
        print("\n" * 2)
        login = input("Login: ")
        password = getpass.getpass("Password: ")

        print("#" * (20 + x))

        cursor = mydb.cursor()

        sql = f"SELECT * FROM userdata WHERE login='{login}'"
        data = (login)
        cursor.execute(sql, data)
        result = cursor.fetchone()
        if result != None:
            login_db = result[0]
            password_db = result[1]
            phone_db = result[4]

            if login_db is None or password_db != password:
                print("\nEither login or password are incorrect. Try again")
                mainMenu()

            else:

                code = generateRandomCode(5)
                print("\nYou have to confirm your phone number, we sent you a code")
                twilioAPI.sendMessage(phone_db, f"Registration code: {code}")
                attempts = 3
                while True:
                    user_code = input("Enter code from your text message: ")
                    if attempts == 0:
                        print("\nToo many atempts, registration incomplete.")
                        mainMenu()
                    elif user_code != code:
                        attempts -= 1
                        print("\nInvalid code, please try again\nRemaining attempts: ", attempts)
                    elif user_code == code:
                        break
                print("\nCode has been confirmed!\n\n")
                logged = True
                logged_user = login
                mainMenu()
        else:
            print("\nEither login or password are incorrect. Try again")
            mainMenu()

    def register():

        config = ConfigParser()
        config.read("config.ini")
        config_variables = config["Settings"]
        name = str(config_variables["name"])
        x = len(name) + 2

        mydb = mysql.connector.connect(
            host=config_variables["host"],
            user=config_variables["user"],
            password=config_variables["password"],
            port=config_variables["port"],
            database=config_variables["database"]
        )

        cursor = mydb.cursor()

        print("#" * (20 + x))
        print("You need to provide following details")
        print("1.Login")
        print("2.Password")
        print("3.Phonenumber")
        print("4.Name")
        print("5.Surename")
        print("#" * (20 + x))

        name = input("Name: ")
        surename = input("Surename: ")

        while True:
            login = input("Login: ")
            sql = f"SELECT * FROM userdata WHERE login='%s'"
            data = (login)
            cursor.execute(sql, data)
            result = cursor.fetchone()
            if result[0] != None:
                print("\nAccount with this login already exists. Please try different one.")
                mainMenu()

        while True:
            password = getpass.getpass("Password: ")
            password_confirm = getpass.getpass("Retype password: ")

            if password != password_confirm:
                print("\nPasswords does not match up.")

            else:
                break
        while True:
            phonenumber = input("Phone number with calling code: ")
            if len(phonenumber) < 13 or len(phonenumber) > 13:
                print("\nIncorrect phonenumber.")

            else:
                break

        code = generateRandomCode(5)
        print("\nYou have to confirm your phonenumber, we sent you a code")
        twilioAPI.sendMessage(phonenumber, f"Registration code: {code}")
        attempts = 3
        while True:
            user_code = input("Enter code from your text message: ")
            if attempts == 0:
                print("\nToo many atempts, registration incomplete.")
                mainMenu()
            elif user_code != code:
                attempts -= 1
                print("\nInvalid code, please try again\nRemaining attempts: ", attempts)
            elif user_code == code:
                break
        print("\nCode has been confirmed!\n\n")

        print("#" * (20 + x))
        print(" " * 10, " {} ".format(name))
        print("#" * (20 + x))
        print()
        print("Name: ", name)
        print("Surename: ", surename)
        print("Password: HIDDEN")
        print("Login: ", login)
        print("Phone number: ", phonenumber)
        print("\n\nDo you want to finish your registeration with those details?\nY/N")
        print("#" * (20 + x))

        while True:
            option = input("--> ").lower()
            if option == "y":
                config = ConfigParser()
                config.read("config.ini")
                config_variables = config["MySQL"]

                mydb = mysql.connector.connect(
                    host=config_variables["host"],
                    user=config_variables["user"],
                    password=config_variables["password"],
                    port=config_variables["port"],
                    database=config_variables["database"]
                )
                sql = ("INSERT INTO userdata(login,password,name,surename,phone) VALUES(%s,%s,%s,%s,%s)")
                person = (login, password, name, surename, phone)
                cursor.execute(sql, person)
                mydb.commit()
                mydb.close()

                print("\nYour registeration is completed. Now you can proceed to log in")
                loginSystem.login()
                break
            elif option == "n":
                print("\nYour registration has been canceled, none of those details is going to be used.")

                break
                mainMenu()
            else:
                print("\nInvalid option, you have to type y for yes or n for no.")


def generateRandomCode(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def mainMenu():
    global logged, logged_user
    config = ConfigParser()
    config.read("config.ini")
    if config.has_section("Settings") == False:
        print("\n\nCould not find a config file, creating one right now!")
        config["Settings"] = {"name": "pyLogIN"}
        with open('config.ini', 'a') as conf:
            config.write(conf)
    if config.has_section("TwilioAPI") == False:
        print("\nCould'nt find a Twilio API config, creating one...")
        token = input("Enter your TwilioAPI token: ")
        account = input("Account ID: ")
        phoneAPI = input("Enter api phone number with calling code: ")

        config["TwilioAPI"] = {"token": token, "account": account, "ApiPhone": phoneAPI}
        with open('config.ini', 'a') as conf:
            config.write(conf)

    if config.has_section("MySQL") == False:
        print("\nI could'nt find a MySQL config, creating one....")
        config["MySQL"] = {"host": "Not set", "user": "not set", "password": "not set", "port": 1000}
        with open('config.ini', 'a') as conf:
            config.write(conf)

    config.read("config.ini")
    config_variables = config["Settings"]
    name = str(config_variables["name"])

    x = len(name) + 2

    if logged == False:
        print("#" * (20 + x))
        print(" " * 10, " {} ".format(name))
        print("#" * (20 + x))
        print()
        print("-Login-")
        print("-Register-")
        print("-Quit-")
        print()
        print("#" * (20 + x))
        option = input("--> ").lower()

        if option == "login":
            loginSystem.login()
        elif option == "register":
            loginSystem.register()
        else:
            print("\n\nInvalid option\n")
            mainMenu()
    elif logged == True:
        print("#" * (20 + x))
        print(" " * 10, " {}".format(name))
        print("#" * (20 + x))
        print("Logged user: ", logged_user)
        print("\n\n-Change password-")
        print("\n")
        print("\n")
        option = input("--> ").lower()
        config = ConfigParser()
        config.read("config.ini")
        config_variables = config["MySQL"]

        if option == "change password":
            mydb = mysql.connector.connect(
                host=config_variables["host"],
                user=config_variables["user"],
                password=config_variables["password"],
                port=config_variables["port"],
                database=config_variables["database"]
            )
            cursor = mydb.cursor()

            current_password = getpass.getpass("\nOld password: ")

            sql = f"SELECT * FROM userdata WHERE login='{logged_user}'"
            cursor.execute(sql)
            result = cursor.fetchone()
            if result[1] != current_password:
                print("\nWrong password! For security reasons you going to be log off.")
                logged = False
                logged_user = ""
                mainMenu()

            if result[1] == current_password:
                while True:
                    new_password = getpass.getpass("New password: ")
                    new_password_confirm = getpass.getpass("Confirm password: ")

                    if new_password != new_password_confirm:
                        print("\nPasswords does not match up.")

                    else:
                        print("\nYour password is going to be updated. Do you want to confirm?")
                        while True:
                            yn = input("Y/N: ")

                            if yn == "y":
                                config = ConfigParser()
                                config.read("config.ini")
                                config_variables = config["MySQL"]
                                mydb = mysql.connector.connect(
                                    host=config_variables["host"],
                                    user=config_variables["user"],
                                    password=config_variables["password"],
                                    port=config_variables["port"],
                                    database=config_variables["database"]
                                )
                                cursor = mydb.cursor()

                                sql = f"UPDATE userdata SET password='{new_password}' WHERE login='{logged_user}'"
                                cursor.execute(sql)
                                mydb.commit()
                                print("\nYour password has been updated, you have to log in again!")
                                logged = False
                                logged_user = ""
                                loginSystem.login()

                            elif yn == "n":
                                print("\nAlright, returning to main menu")
                                mainMenu()
                            else:
                                print("\nInvalid option, type y/n")







if __name__ == "__main__":
    mainMenu()
