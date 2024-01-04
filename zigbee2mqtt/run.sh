docker run -d\
   --name zigbee2mqtt \
   --restart=unless-stopped \
   --network=host \
   --device=/dev/serial/by-id/usb-ITEAD_SONOFF_Zigbee_3.0_USB_Dongle_Plus_V2_20220718170458-if00:/dev/ttyACM0 \
   -v $(pwd)/data:/app/data \
   -v /run/udev:/run/udev:ro \
   -e TZ=Europe/Warsaw \
   koenkk/zigbee2mqtt
