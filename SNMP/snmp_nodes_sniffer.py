import os
import subprocess
import time
from influxdb import InfluxDBClient
from datetime import datetime


docker_manager = "tcp://10.2.0.1:2375"
docker_stack = "misago"
influx_db_host = '10.5.0.109'
influx_db_port = 8086
influx_db_db = "telegraf"
client = None

oids = [
    ("DISMAN-EVENT-MIB::sysUpTimeInstance","uptime"), 
    ("SNMPv2-MIB::sysName.0","hostname"),
    ("SNMPv2-MIB::sysLocation.0","location"),
    ("UCD-SNMP-MIB::ssIOSent.0","IOSent"),
    ("UCD-SNMP-MIB::ssIOReceive.0","IOReceive"),
    ("UCD-SNMP-MIB::ssCpuUser.0","CpuUserPercentage"),
    ("UCD-SNMP-MIB::ssCpuSystem.0","CpuSystemPercentage"),
    ("UCD-SNMP-MIB::ssCpuIdle.0", "CpuIdlePercentage"),
    ("UCD-SNMP-MIB::memTotalReal.0", "TotalRAM"),
    ("UCD-SNMP-MIB::memAvailReal.0", "AvailableRAM"),
    ("UCD-SNMP-MIB::memTotalFree.0", "FreeRAM"),
    ("UCD-SNMP-MIB::dskTotal.1", "TotalDiskSpace"),
    ("UCD-SNMP-MIB::dskUsed.1", "TotalDiskUsed"),
    ("UCD-SNMP-MIB::dskAvail.1", "TotalDiskAvailable"),
    ("UCD-SNMP-MIB::dskPercent.1","DiskUsagePercentage")
    ]


to_execute = "export DOCKER_HOST=\"" + docker_manager + "\" && docker stack ps " + docker_stack + "| grep Running | awk '{print $2  \"\\t\" $4}'"


def process_output_type(output):
    # get type of the output
    output_type = output.split("=")[1].split(":")[0].strip()
    output_value = output.split("=")[1].split(":")[1].strip()

    if output_type == "INTEGER":
        return int(''.join([s for s in output_value if s.isdigit()]))
    elif output_type == "Timeticks":
        return int(output_value.split("(")[1].split(")")[0])
    return output_value
  

while True:
    try:
        # Connecct to DB
        if client == None:
            client = InfluxDBClient(host=influx_db_host, port=influx_db_port)
            client.switch_database(influx_db_db)

        # get the computes in the database
        result_set = client.query("SHOW TAG VALUES ON telegraf FROM snmp WITH KEY = \"hostname\";")
        computes_in_db =  [v[1] for v in result_set.raw['series'][0]['values']]
        print("computes_in_db", computes_in_db)

        # get the computes that are being used
        computes_being_used = []
        computes_being_used_ips = []
        output = subprocess.check_output(to_execute, shell=True).decode("utf-8")
        for line in output.split("\n")[:-1]:    
            service, compute_location = line.strip().split("\t")
            compute_ip = "10.{}.0.{}".format(compute_location[-3], ''.join(compute_location[-2:]))
            computes_being_used.append(compute_location)
            computes_being_used_ips.append(compute_ip)

        print("computes_being_used", computes_being_used)
        print("computes_being_used_ips", computes_being_used_ips)

        # find the computes that stopped being used
        computes_not_being_used_anymore = set(computes_in_db).difference(set(computes_being_used))

        # remove these computes from the database
        all_metrics_to_be_added = []
        for compute in computes_not_being_used_anymore:
            print("Removing compute",compute, "...")
            client.query(f"DROP SERIES FROM snmp WHERE hostname='{compute}';")
        

        # the metrics will be updated 20 times, 1 time each 15 seconds
        for run in range(0,20):
            # get all snmp data
            for ip in computes_being_used_ips:
                valid = True

                # data that will be added to influx db
                data_to_add = {
                    "measurement":"snmp",
                    "tags": {},
                    "time": datetime.now(),
                    "fields": {}
                }

                # get all snmp values
                for oid in oids:
                    try:
                        output = subprocess.check_output(f"snmpget -v 2c -c gicgirs  {ip} {oid[0]}", shell=True).decode("utf-8")
                        output_value = process_output_type(output.strip())
                        data_to_add["fields"][oid[1]] = output_value
                    except:
                        print("Error on", ip)
                        valid = False

                    # if a rogue node is found
                    if not valid:
                        break

                # correct the tag 
                if "hostname" in data_to_add["fields"]:
                    data_to_add["tags"]["hostname"] = data_to_add["fields"]["hostname"]
                    del data_to_add["fields"]["hostname"]
                    print("Write points:", data_to_add)
                    all_metrics_to_be_added.append(data_to_add)
                

            # add all metrics to influx db  
            client.write_points([data_to_add])

            #wait for next iteration
            print("Sleeping...\n\n")
            time.sleep(15)

    except Exception as e:
        print("Exception",e)