docker run -d \
   --name mosquitto \
   --restart=unless-stopped \
   --network=host \
   -v $(pwd)/config:/mosquitto/config:rw \
   -v $(pwd)/data:/mosquitto/data:rw \
   -e TZ=Europe/Warsaw \
   eclipse-mosquitto
