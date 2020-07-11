i=0

while [ $i -lt 50 ]
do
eval "locust -f register_users.py -u 100 -r 5 --host=http://10.2.0.1:6360 --headless"
i=$[$i+1]
sleep 10
done