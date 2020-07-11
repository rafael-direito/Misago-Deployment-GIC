import os
import subprocess
from os import path
from datetime import datetime
import time
import sys

docker_manager = "tcp://10.2.0.1:2375"

# assert that teh params have been passed
assert len(sys.argv) == 4

operation = sys.argv[1]
docker_service = sys.argv[2]
operation_timestamp_file_path = sys.argv[3]

# assert that the operation is correct
assert operation in ["scale", "descale"]

# find number of replicas of service
to_execute = f"export DOCKER_HOST=\"{docker_manager}\" && docker service ls | grep {docker_service}"

# get number of replicas being executed
output = subprocess.check_output(to_execute, shell=True).decode("utf-8")
replicas = int(output.strip().split()[3].split("/")[0])


# if we are trying to descale a service wiht only 1 replica - leave
if replicas < 2 and operation == "descale" :
    print("Wont descale a service with 1 replica!")
    exit(0)


may_scale_or_descale = True
# check when was the last scale/descale down
if os.path.isfile(operation_timestamp_file_path):
    operation_timestamp_file = open(operation_timestamp_file_path)
    last_op_date_str = operation_timestamp_file.readline().strip()
    operation_timestamp_file.close()

    last_op_date = datetime.strptime(last_op_date_str, "%d-%b-%Y %H:%M:%S")
    # get current time
    now = datetime.now()
    # get seconds from the last operation
    diff = now - last_op_date
    duration_in_s = diff.total_seconds() 
    if duration_in_s < 5 * 60:
        may_scale_or_descale = False


# scale or descale
if may_scale_or_descale:
    # compute new number of replicas
    updated_replicas = replicas - 1 if operation == "descale" else replicas + 1

    # scale or descale service
    print(f"Operation {operation}, on {docker_service} ...")
    to_execute = f"export DOCKER_HOST=\"{docker_manager}\" && docker service scale {docker_service}={updated_replicas}"
    subprocess.check_output(to_execute, shell=True)

    print(f"Operation {operation} on {docker_service} has been completed. This service now has {updated_replicas} replicas!")

    # save timestamp to file
    now_str = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    operation_timestamp_file = open(operation_timestamp_file_path, "w")
    operation_timestamp_file.write(now_str)
    operation_timestamp_file.close()
else:
    print("The last operation was committed too recently!")
