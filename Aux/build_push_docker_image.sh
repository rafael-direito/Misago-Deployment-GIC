# $1 path to image 
# $2 image name

echo $1
echo $2

eval "export DOCKER_HOST='tcp://10.2.0.1:2375'"

# build image
echo "building image"
eval "docker build $1 -t $2"

# new tag
echo "new tag"
eval "docker tag $2 10.2.0.1:5000/$2:latest"

# push image
echo "push image"
eval "docker push 10.2.0.1:5000/$2:latest"

