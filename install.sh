#!/usr/bin/env bash
set -x
[ -d foo ] || mkdir work
sudo apt update
sudo apt install -o Dpkg::Options::="--force-confold" -y mpd
sudo apt install -y mpc
sudo cp src/mpd.conf /etc/mpd.conf
sudo cp src/mpd.service /etc/systemd/system/
sudo chown root:root /etc/systemd/system/mpd.service
sudo systemctl daemon-reload
sudo systemctl enable mpd
sudo systemctl start mpd
sudo cp src/rp_crontab /etc/cron.d/rp_crontab
sudo chown root:root /etc/cron.d/rp_crontab
sudo systemctl restart cron

sudo cp src/gpiod.service /etc/systemd/system/
sudo chown root:root /etc/systemd/system/gpiod.service
sudo systemctl daemon-reload
sudo systemctl enable gpiod
sudo systemctl start gpiod


wget https://github.com/Spotifyd/spotifyd/releases/download/v0.3.3/spotifyd-linux-armv6-slim.tar.gz -O work/spotifyd-linux-armv6-slim.tar.gz
tar -xzvf work/spotifyd-linux-armv6-slim.tar.gz work/
chmod 755 work/spotifyd
mkdir -p /home/pi/.config/spotifyd
touch /home/pi/.config/spotifyd/spotifyd.conf
sudo cp src/spotifyd.service /etc/systemd/system/
sudo chown root:root /etc/systemd/system/spotifyd.service
sudo systemctl daemon-reload
sudo systemctl enable spotifyd
sudo systemctl start spotifyd
