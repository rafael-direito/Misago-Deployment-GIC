#!/bin/bash


# 1. Register users
#echo "Registering $NUM_CLIENTS ..."
#eval "locust -f register_users.py -u $NUM_CLIENTS -r $HATCH_RATE_REGISTER --host=http://$TARGET_ADDRESS:$TARGET_PORT --headless"
#echo "$NUM_CLIENTS clients registered!"


# 2. Run the UI in the browser
echo "Opening locust interface..."
eval "locust -f lifecycle.py"

#NUM_TASKS_PER_CLIENT_IN_TEST