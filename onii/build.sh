#!/bash/sh

cd /home/build/onii/

docker build -t onii:0.1 /home/build/onii/

docker save onii:0.1 > /home/build/onii-0.1.tar

