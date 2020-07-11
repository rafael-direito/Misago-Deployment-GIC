from locust import HttpUser, task, between, runners
import random
import string
import time

published_threads_urls = []
user_credentials = []
user_index = 0
user_pool_size = 10
num_curr_users = 0

# open file to record the user credentials
user_file = open("/user_data/user_data.tsv")
for line in user_file:
    line = line.strip()
    m_username, m_email, m_password = line.split("\t")
    user_credentials.append((m_username, m_email, m_password))

#print(user_credentials)


class QuickstartUser(HttpUser):
    
    wait_time = between(30,30)
    num_tasks_handled = 0
    MAX_TASKS_COUNT = 50

    is_writter = False

    def on_start(self):        
        """ 
        on_start is called when a Locust start before any task is scheduled
        """
        global num_curr_users
        global user_pool_size

        num_curr_users +=1

        if random.randint(1, 100+1) <= 15:
            # open website
            self.base_access()

            # log in the user 
            m_username, m_email, m_password = self.get_user_credentials()
            self.log_user(m_username, m_email, m_password)

            self.is_writter = True

        # wait for all the users to be logged in
        #while num_curr_users < user_pool_size:
        #    time.sleep(1)

        # wait a bit before starting the tests
        #print("Sleeping")
        #time.sleep(15)
        #print("Im done with sleeping")



    def get_user_credentials(self):
        global user_index
        global user_credentials
   
        user_index = user_index + 1 if user_index < len(user_credentials) - 2 else 0
        return user_credentials[user_index]


    def base_access(self):
        self.client.get("/")
        self.client.get("/static/misago/css/misago.css")
        #self.client.get("/django-i18n.js?en-us")
        #self.client.get("/static/misago/js/vendor.js")
        #self.client.get("/static/misago/js/misago.js")
        #self.client.get("/static/debug_toolbar/css/print.css")
        #self.client.get("/static/debug_toolbar/css/toolbar.css")
        #self.client.get("/static/debug_toolbar/js/toolbar.js")
        #self.client.get("/api/threads/?category=2&list=all")
        #self.client.get("/static/misago/apple-touch-icon.png")
        #self.client.get("/static/misago/favicon-16.png")

    

    def log_user(self, m_username, m_email, m_password):
        # get session cookies
        print("[Log In new user]", self.client.cookies.get_dict())
        csrftoken = self.client.cookies.get_dict()["csrftoken"]

        print (m_username, m_email, m_password)
        print("[Log In new user] Trying to authenticate a user...")

        response = self.client.post("/api/auth/",
                         json = {"username": m_username,
                          "password": m_password}, 
                          headers={"X-CSRFToken" : csrftoken})
        
        print("[Log In new user] Sucess:", response.status_code == 200)

        # useless data - only for load testing purposes
        #self.client.get("/?ref=login")
        #self.client.get("/static/misago/css/misago.css")
        #self.client.get("/django-i18n.js?en-us")
        #self.client.get("/static/misago/js/vendor.js")
        #self.client.get("/static/misago/js/misago.js")
        #self.client.get("/static/debug_toolbar/css/print.css")
        #self.client.get("/static/debug_toolbar/css/toolbar.css")
        #self.client.get("/static/debug_toolbar/js/toolbar.js")
        #self.client.get("/api/threads/?category=2&list=all")
        #self.client.get("/static/misago/apple-touch-icon.png")
        #self.client.get("/static/misago/favicon-16.png")
        #self.client.get("/static/misago/apple-touch-icon.png")
        

    @task(5)
    def write_thread(self):
        if not self.is_writter:
            return

        # useless data - only for load testing purposes
        self.client.get("/api/threads/editor/")

        # get session cookies
        csrftoken = self.client.cookies.get_dict()["csrftoken"]

        # write thread
        thread_title = ''.join(random.choice(string.ascii_lowercase) for i in range(random.randint(8, 16)))
        thread_content = ''.join(random.choice(string.ascii_lowercase) for i in range(random.randint(40, 200)))
        thread_category = 3
        response = self.client.post("/api/threads/",
                         json = {"title": thread_title,
                          "post": thread_content,
                          "category": thread_category,
                          "attachments": [],
                          "close" : "false",
                          "hide" : "false",
                          "pin" : 0}, headers={"X-CSRFToken" : csrftoken})

        # get thread infos
        json_response_dict = response.json()
        thread_id = json_response_dict['id']
        thread_url = json_response_dict['url']

        # append to published threads
        published_threads_urls.append(thread_url)

        # useless data - only for load testing purposes
        #self.client.get(thread_url)
        #self.client.get("/static/misago/css/misago.css")
        #self.client.get("/django-i18n.js?en-us")
        #self.client.get("/static/misago/js/vendor.js")
        #self.client.get("/static/misago/js/misago.js")
        #self.client.get("/static/debug_toolbar/css/print.css")
        #self.client.get("/static/debug_toolbar/css/toolbar.css")
        #self.client.get("/static/debug_toolbar/js/toolbar.js")
        #self.client.get("/static/debug_toolbar/img/ajax-loader.gif")
        #self.client.get("/static/debug_toolbar/img/djdt_vertical.png")
        #self.client.get("/static/misago/apple-touch-icon.png")
        #self.client.get("/static/misago/favicon-32.png")
       
        self.num_tasks_handled += 1
        self.check_id_should_die()
        
    @task(3)
    def subscribe_thread(self):
        # if we have no threads in the system, ignore this step
        if len(published_threads_urls) == 0  or not self.is_writter:
            return

        # get a thread to which we will reply
        thread_url = random.choice(published_threads_urls)
        thread_id = thread_url.split("/")[-2]

        # get session cookies
        csrftoken = self.client.cookies.get_dict()["csrftoken"]

        # Subscribe to thread
        response = self.client.patch(f"/api/threads/{thread_id}/",
                        json = [{"op" : "replace" ,
                        "path": "subscription",
                        "value" : "notify"}], headers={"X-CSRFToken" : csrftoken})
        print("Subscribed:", response.status_code)

        self.num_tasks_handled += 1
        self.check_id_should_die()


    @task(7)
    def reply_thread(self):
        # if we have no threads in the system, ignore this step
        if len(published_threads_urls) == 0 or not self.is_writter:
            return

        # get a thread to which we will reply
        thread_url = random.choice(published_threads_urls)
        thread_id = thread_url.split("/")[-2]

        # get session cookies
        csrftoken = self.client.cookies.get_dict()["csrftoken"]

        # Subscribe to thread
        self.client.get(f"/api/threads/{thread_id}/posts/reply_editor/")

        # post reply
        answer_text =  ''.join(random.choice(string.ascii_lowercase) for i in range(random.randint(40, 250)))
        response = self.client.post(f"/api/threads/{thread_id}/posts/",
                        json = {"post" : answer_text ,"attachments":[]}, headers={"X-CSRFToken" : csrftoken})

        # load interface
        # get answer id
        json_response_dict = response.json()
        reply_id = json_response_dict['id']

        self.num_tasks_handled += 1
        self.check_id_should_die()



    @task(75)
    def consult_thread(self):
        # if we have no threads in the system, ignore this step
        if len(published_threads_urls) == 0:
            return

        # get a thread to which we will reply
        thread_url = random.choice(published_threads_urls)
        thread_id = thread_url.split("/")[-2]

        # get the thread
        self.client.get(f"/api/threads/{thread_id}/")

        # get session cookies
        #csrftoken = self.client.cookies.get_dict()["csrftoken"]

        # useless data - only for load testing purposes
        #self.client.get("/static/misago/css/misago.css")
        #self.client.get("/django-i18n.js?en-us")
        #self.client.get("/static/misago/js/vendor.js")
        #self.client.get("/static/misago/js/misago.js")
        #self.client.get("/static/debug_toolbar/css/print.css")
        #self.client.get("/static/debug_toolbar/css/toolbar.css")
        #self.client.get("/static/debug_toolbar/js/toolbar.js")
        #self.client.get("/static/debug_toolbar/img/ajax-loader.gif")
        #self.client.get("/static/debug_toolbar/img/djdt_vertical.png")
        #self.client.get("/static/misago/apple-touch-icon.png")

        '''
        # USER SUBSCRIBES THE THREAD 15% OF THE TIME
        if random.randint(1, 100+1) <= 15:
            response = self.client.patch(f"/api/threads/{thread_id}/",
                            json = [{"op" : "replace" ,
                            "path": "subscription",
                            "value" : "notify"}], headers={"X-CSRFToken" : csrftoken})
            print("Subscribed:", response.status_code)


        #  USER REPLIES TO THE THREAD 10% OF THE TIME
        if random.randint(1, 100+1) <= 10:
            self.client.get(f"/api/threads/{thread_id}/posts/reply_editor/")

            # post reply
            answer_text =  ''.join(random.choice(string.ascii_lowercase) for i in range(random.randint(40, 250)))
            response = self.client.post(f"/api/threads/{thread_id}/posts/",
                            json = {"post" : answer_text ,"attachments":[]}, headers={"X-CSRFToken" : csrftoken})

            # load interface
            # get answer id
            json_response_dict = response.json()
            reply_id = json_response_dict['id']

            #self.client.get(thread_url + f"post/{reply_id}/")
            #self.client.get(thread_url + f"#post-{reply_id}")

            # useless data - only for load testing purposes
            #self.client.get("/static/misago/css/misago.css")
            #self.client.get("/django-i18n.js?en-us")
            #self.client.get("/static/misago/js/vendor.js")
            #self.client.get("/static/misago/js/misago.js")
            #self.client.get("/static/debug_toolbar/css/print.css")
            #self.client.get("/static/debug_toolbar/css/toolbar.css")
            #self.client.get("/static/debug_toolbar/js/toolbar.js")
            #self.client.get("/static/debug_toolbar/img/ajax-loader.gif")
            #self.client.get("/static/debug_toolbar/img/djdt_vertical.png")
            #self.client.get("/static/misago/apple-touch-icon.png")
            #self.client.get("/static/misago/favicon-32.png")
            # Error, even on the service
            #self.client.post(f"/api/threads/{thread_id}/posts/{reply_id}/read/",json = {"thread_is_read": True}, headers={"X-CSRFToken" : csrftoken})
        '''

        self.num_tasks_handled += 1
        self.check_id_should_die()


    @task(1)
    def check_my_threads(self):
        if not self.is_writter:
            return
        # get session cookies
        csrftoken = self.client.cookies.get_dict()["csrftoken"]
        self.client.get("/api/threads/?category=2&list=my&start=0")
        self.client.get("/api/threads/?category=2&list=my")
        print("check_my_threads")
        self.num_tasks_handled += 1
        self.check_id_should_die()


    @task(3)
    def check_new_threads(self):
        if not self.is_writter:
            return
        # get session cookies
        csrftoken = self.client.cookies.get_dict()["csrftoken"]
        self.client.get("/api/threads/?category=2&list=new&start=0")
        self.client.get("/api/threads/?category=2&list=new")
        print("check_new_threads")
        self.num_tasks_handled += 1
        self.check_id_should_die()


    @task(3)
    def check_unread_threads(self):
        if not self.is_writter:
            return
        # get session cookies
        csrftoken = self.client.cookies.get_dict()["csrftoken"]
        self.client.get("/api/threads/?category=2&list=unread&start=0")
        self.client.get("/api/threads/?category=2&list=unread")
        print("check_unread_threads")
        self.num_tasks_handled += 1
        self.check_id_should_die()


    @task(3)
    def check_subscribed_threads(self):
        if not self.is_writter:
            return
        # get session cookies
        csrftoken = self.client.cookies.get_dict()["csrftoken"]
        self.client.get("/api/threads/?category=2&list=subscribed&start=0")
        self.client.get("/api/threads/?category=2&list=subscribed")
        print("check_subscribed_threads")
        self.num_tasks_handled += 1
        self.check_id_should_die()


    
    def check_id_should_die(self):
        if self.num_tasks_handled >= self.MAX_TASKS_COUNT:
            print("STOPPING")
            time.sleep(60*60*24)

