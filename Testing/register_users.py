from locust import HttpUser, task, TaskSet, between
import random
import string
import time


user_pool_size = 100
num_curr_users = 0

class RegisterNewUsers(HttpUser):
    wait_time = between(0.9,1)

    @task
    class Register(TaskSet):
        wait_time = between(0.9,1)
        def on_start(self):
            """ 
            on_start is called when a Locust start before any task is scheduled
            """

            global num_curr_users
            global user_pool_size

            # open file to record the user ccredeentials
            self.user_file = open("user_data.tsv", "a+")

            # open website
            self.client.get("/")

            # register new user
            self.register_new_user()

            num_curr_users +=1
            print(num_curr_users)
            # wait for all the users to be signed in
            while num_curr_users < user_pool_size:
                time.sleep(3)

            exit(0)


        def register_new_user(self):
            # useless data - only for load testing purposes
            self.client.get("/api/auth/criteria/")
            self.client.get("/static/misago/js/zxcvbn.js")
            
            # get session cookies
            csrftoken = self.client.cookies.get_dict()["csrftoken"]

            # generate new  user data
            m_username = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
            m_password = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
            m_email = m_username + "@ua.pt"

            
            
            # register new user
            response = self.client.post("/api/users/",
                            json = {"username": m_username,
                            "email": m_email,
                            "password": m_password,
                            "captcha": "",
                            "terms_of_service" : None,
                            "privacy_policy" : None}, headers={"X-CSRFToken" : csrftoken})

            print("[Register new user] Satus Code:", response.status_code)

            if response.status_code == 200:
                print("[Register new user] Username:", m_username)
                print("[Register new user] Email:", m_email)
                print("[Register new user] Password:", m_password)

                # write data to file
                self.user_file.write(f"{m_username}\t{m_email}\t{m_password}\n")
                self.user_file.flush()
            
            return m_username, m_email, m_password

        @task
        def stop(self):
            print("STOPPING")
            time.sleep(60*60*24)
