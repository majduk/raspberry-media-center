#!/usr/bin/env bash
set -x

[ -d foo ] || mkdir work
sudo apt update

# Installing PulseAudio
sudo apt install -y --no-install-recommends pulseaudio
sudo usermod -a -G pulse-access root
sudo mv /etc/pulse/client.conf /etc/pulse/client.conf.orig
sudo cp src/pulse/client.conf /etc/pulse/client.conf
sudo cp src/pulse/daemon.conf /etc/pulse/daemon.conf
sudo cp src/pulse/default.pa /etc/pulse/default.pa
sudo cp src/pulse/system.pa /etc/pulse/system.pa
sudo cp src/pulseaudio.service /etc/systemd/system/pulseaudio.service
sudo chown root:root /etc/systemd/system/pulseaudio.service
sudo mv /etc/alsa/conf.d/50-pulseaudio.conf{,.orig}
sudo mv /etc/alsa/conf.d/99-pulse.conf{,.orig}
sudo cp src/99-pulseaudio.conf /etc/alsa/conf.d/99-pulseaudio.conf
sudo chown root:root /etc/alsa/conf.d/99-pulseaudio.conf
sudo systemctl enable --now pulseaudio.service
sudo systemctl --global mask pulseaudio.socket

# Setting up bluetooth
sudo apt install -y --no-install-recommends bluez-tools pulseaudio-module-bluetooth
sudo cp src/bluetooth/main.conf /etc/bluetooth/main.conf
sudo mkdir -p /etc/systemd/system/bthelper@.service.d
sudo cp src/bluetooth/override.conf /etc/systemd/system/bthelper@.service.d/override.conf
sudo chown root:root /etc/systemd/system/bthelper@.service.d/override.conf
sudo cp src/bluetooth/bt-agent@.service /etc/systemd/system/bt-agent@.service
sudo chown root:root /etc/systemd/system/bt-agent@.service
systemctl daemon-reload
systemctl enable bt-agent@hci0.service
sudo usermod -a -G bluetooth pulse

# Installing MPD
sudo apt install -o Dpkg::Options::="--force-confold" -y mpd
sudo apt install -y mpc
sudo usermod -a -G pulse-access mpd
sudo cp src/mpd.conf /etc/mpd.conf
sudo cp src/mpd.service /etc/systemd/system/
sudo chown root:root /etc/systemd/system/mpd.service
sudo systemctl daemon-reload
sudo systemctl enable mpd
sudo systemctl start mpd
sudo cp src/rp_crontab /etc/cron.d/rp_crontab
sudo chown root:root /etc/cron.d/rp_crontab
sudo systemctl restart cron
sudo cp src/radio.mpl.m3u /var/lib/mpd/playlists/radio.mpl.m3u
sudo chown mpd:audio /var/lib/mpd/playlists/radio.mpl.m3u

# Installing GPIO
sudo cp src/gpiod.service /etc/systemd/system/
sudo chown root:root /etc/systemd/system/gpiod.service
sudo systemctl daemon-reload
sudo systemctl enable gpiod
sudo systemctl start gpiod

# Installing Spotifyd
wget https://github.com/Spotifyd/spotifyd/releases/download/v0.3.3/spotifyd-linux-armv6-slim.tar.gz -O work/spotifyd-linux-armv6-slim.tar.gz
tar -xzvf work/spotifyd-linux-armv6-slim.tar.gz work/
chmod 755 work/spotifyd
mkdir -p /home/pi/.config/spotifyd
touch /home/pi/.config/spotifyd/spotifyd.conf
cp src/spotifyd.conf /home/pi/.config/spotifyd/spotifyd.conf
sudo cp src/spotifyd.service /etc/systemd/system/
sudo chown root:root /etc/systemd/system/spotifyd.service
sudo systemctl daemon-reload
sudo systemctl enable spotifyd
sudo systemctl start spotifyd

# Installing Pulsemixer
curl https://raw.githubusercontent.com/GeorgeFilipkin/pulsemixer/master/pulsemixer > pulsemixer && chmod +x ./pulsemixer
