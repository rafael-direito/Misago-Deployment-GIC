import re

possible_actions =  {
    "login": ["/api/auth/", "/?ref=login", "/static/misago/css/misago.css", "/django-i18n.js?en-us", "/static/misago/js/vendor.js", "/static/misago/js/misago.js", "/static/debug_toolbar/css/print.css", "/static/debug_toolbar/css/toolbar.css", "/static/debug_toolbar/js/toolbar.js", "/api/threads/?category=2&list=all", "/static/misago/apple-touch-icon.png", "/static/misago/favicon-16.png", "/static/misago/apple-touch-icon.png"],
    "write_thread": ["/t/\w+/[0-9]+/post/[0-9]+/"] + ["/api/threads/editor/", "/api/threads/", "/static/misago/css/misago.css",  "/django-i18n.js?en-us",  "/static/misago/js/vendor.js",  "/static/misago/js/misago.js",  "/static/debug_toolbar/css/print.css",  "/static/debug_toolbar/css/toolbar.css",  "/static/debug_toolbar/js/toolbar.js",  "/static/debug_toolbar/img/ajax-loader.gif",  "/static/debug_toolbar/img/djdt_vertical.png",  "/static/misago/apple-touch-icon.png",  "/static/misago/favicon-32.png"],
    "read_thread": ["/t/\w+/[0-9]+/"] + ["/static/misago/css/misago.css", "/django-i18n.js?en-us", "/static/misago/js/vendor.js", "/static/misago/js/misago.js", "/static/debug_toolbar/css/print.css", "/static/debug_toolbar/css/toolbar.css", "/static/debug_toolbar/js/toolbar.js", "/static/debug_toolbar/img/ajax-loader.gif", "/static/debug_toolbar/img/djdt_vertical.png", "/static/misago/apple-touch-icon.png"],
    "subscribe_thread": ["/api/threads/[0-9]+/"] + ["/t/\w+/[0-9]+/post/[0-9]+/"] + ["/static/misago/css/misago.css", "/django-i18n.js?en-us", "/static/misago/js/vendor.js", "/static/misago/js/misago.js", "/static/debug_toolbar/css/print.css", "/static/debug_toolbar/css/toolbar.css", "/static/debug_toolbar/js/toolbar.js", "/static/debug_toolbar/img/ajax-loader.gif", "/static/debug_toolbar/img/djdt_vertical.png", "/static/misago/apple-touch-icon.png"],
    "reply_thread": ["/api/threads/[0-9]+/posts/reply_editor/", "/api/threads/[0-9]+/posts/", "/t/\w+/[0-9]+/post/[0-9]+/"]  + ["/static/misago/css/misago.css",  "/django-i18n.js?en-us",  "/static/misago/js/vendor.js",  "/static/misago/js/misago.js",  "/static/debug_toolbar/css/print.css",  "/static/debug_toolbar/css/toolbar.css",  "/static/debug_toolbar/js/toolbar.js",  "/static/debug_toolbar/img/ajax-loader.gif",  "/static/debug_toolbar/img/djdt_vertical.png",  "/static/misago/apple-touch-icon.png",  "/static/misago/favicon-32.png"] + ["/t/\w+/[0-9]+/post/[0-9]+/"] + ["/static/misago/css/misago.css", "/django-i18n.js?en-us", "/static/misago/js/vendor.js", "/static/misago/js/misago.js", "/static/debug_toolbar/css/print.css", "/static/debug_toolbar/css/toolbar.css", "/static/debug_toolbar/js/toolbar.js", "/static/debug_toolbar/img/ajax-loader.gif", "/static/debug_toolbar/img/djdt_vertical.png", "/static/misago/apple-touch-icon.png"],
    "check_my_threads": ["/api/threads/?category=2&list=my&start=0", "/api/threads/?category=2&list=my"],
    "check_new_threads": ["/api/threads/?category=2&list=new&start=0", "/api/threads/?category=2&list=new"],
    "check_unread_threads": ["/api/threads/?category=2&list=unread&start=0", "/api/threads/?category=2&list=unread"],
    "check_subscribed_threads": ["/api/threads/?category=2&list=subscribed&start=0", "/api/threads/?category=2&list=subscribed"]
    }


test_output_data_file = open("results/requests_1500_users.csv")
test_output_data = []

test_output_data_file.readline()
for line in test_output_data_file:
    line = line.strip()
    line_splitted = line.split(",")
    call, median_time, avg_time, min_time, max_time, req_count, req_fail = line_splitted[1], float(line_splitted[4]), float(line_splitted[5]), float(line_splitted[6]), float(line_splitted[7]), float(line_splitted[2]),float(line_splitted[3])
    tup = (call, (median_time, avg_time, min_time, max_time, req_count, req_fail))
    test_output_data.append(tup)


calls = possible_actions["read_thread"] #"/api/threads/?category=2&list=unread&start=0", "/api/threads/?category=2&list=unread"]

for action, calls in possible_actions.items():
    action_data = [0, 0, 0, 0, 0, 0]
    for call in calls:
        call_re = call.replace("?", "\?")
        # avg_time, min_time, max_time, req_count, req_fail, NUM_ENTRIES
        data = [0, 0, 0, 0, 0, 0, 0]
        for test_tup in test_output_data:
            match_object = re.search(call_re, test_tup[0])    
            if match_object != None and match_object.span()[1] - match_object.span()[0] == len(test_tup[0]):
                data[0] += test_tup[1][0]
                data[1] += test_tup[1][1]
                data[2] += test_tup[1][2]
                data[3] += test_tup[1][3]
                data[4] += test_tup[1][4]
                data[5] += test_tup[1][5]
                data[5] += 1

        # normalize
        if data != [0, 0, 0, 0, 0, 0, 0]:
            data[0] = data[0] / data[5]
            data[1] = data[1] / data[5]
            data[2] = data[2] / data[5]
            data[3] = data[3] / data[5]
            data[4] = data[4] 
            data[5] = data[5] 

            action_data[0] += data[0]
            action_data[1] += data[1]
            action_data[2] += data[2]
            action_data[3] += data[3]
            action_data[4] += data[4]
            action_data[5] += data[5]

    # to seconds
    action_data[0] = action_data[0]/1000
    action_data[1] = action_data[1]/1000
    action_data[2] = action_data[2]/1000
    action_data[3] = action_data[3]/1000
    print(action,"->",action_data)

