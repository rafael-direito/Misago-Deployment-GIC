#!/bin/bash



# 1. Collect static files
#echo "Collecting static files..."
#eval "rm -rf /srv/misago/devproject/static"
#eval "python manage.py collectstatic"
#echo "Collected static files!"

# Function to load secrets
file_env() {
  local var="$1"
  local fileVar="${var}_FILE"
  echo $fileVar
  fileLocation=$(printenv  $fileVar)
  if [ -f "$fileLocation" ]; then
    echo "$fileLocation exist"
    val=$(cat $fileLocation)
    echo "The secret associated with " $var "is " $val "!"
    export "$var"="$val"
  fi
}

file_env 'POSTGRES_PASSWORD'
file_env 'SUPERUSER_PASSWORD_FILE'

# save ip in an environment variable
export HOST_IP=$HOST_MONITORING_TAG$(awk 'END{print $1}' /etc/hosts) 
# Run metric collector - telegraf
eval "/usr/bin/telegraf --config /telegraf.conf &"

# 2. Able to populate the Database?
echo "Migrating database..."

num_connections=0
while true; 
do
  echo "Attemp $num_connections..."
  eval "python manage.py migrate"
  if [ $? -eq 0 ]; then
    echo "Successfuly migrated data!"
    break  
  fi
  echo "Couldnt migrated data!"
  # it too many attempts
  if [ $num_connections -gt 4 ] ; then
    echo "Leaving -  migrated data!"
    exit 1
  fi
  # increment number of attempts and sleep
  ((num_connections=num_connections+1))
  sleep 10
done


# 3. Running celery 
echo "Running Celery..."

num_connections_celery=0
while true; 
do
  echo "Attemp $num_connections..."
  eval "celery -A devproject worker --loglevel=info --detach"
  if [ $? -eq 0 ]; then
    echo "Successfuly lauched Celery!"
    break
  fi
  # it too many attempts
  if [ $num_connections_celery -gt 4 ] ; then
    exit 1
  fi
  # increment number of attempts and sleep
  ((num_connections_celery=num_connections_celery+1))
  sleep 5
done

echo "All done in the entrypoint"
# 4. Run Gunicorn
echo "Running Gunicorn..."

#"python manage.py runserver 0.0.0.0:80" #
#eval "gunicorn -b 0.0.0.0:80 --workers 5 devproject.wsgi:application --access-logfile '-' --error-logfile '-'"

eval "gunicorn -b 0.0.0.0:80 --workers 5 devproject.wsgi:application --access-logformat  'Host:%(h)s %(l)s Username:%(u)s DateOfRequest:%(t)s Method:%(m)s Status:%(s)s URL:%(U)s ReponseLength:%(B)s Agent:%(a)s  ResponseHeader:%({server-timing}o)s' --access-logfile '-' --error-logfile '-'"
if [ $? -eq 0 ]; 
then
  echo "Successfuly lauched Gunicorn server!"
else
  echo "Error on lauching Gunicorn server!"
  exit 1
fi