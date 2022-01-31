#!/usr/bin/env bash

[ -d foo ] || mkdir -p work

install_base () {
  sudo apt update
  sudo apt install -y python3-pip
  sudo apt install -y bridge-utils
  curl -sSL https://get.docker.com | sh
  sudo usermod -aG docker ${USER}
  sudo systemctl enable docker
}

configure_network () {
  sudo cp etc/network/interfaces.d/00-br0 /etc/network/interfaces.d/00-br0
  sudo chown root:root /etc/network/interfaces.d/00-br0
  sudo service networking restart
}

install_pulseaudio () {
  sudo apt install -y --no-install-recommends pulseaudio
  sudo usermod -a -G pulse-access root
  sudo pip3 install pulsectl
  curl https://raw.githubusercontent.com/GeorgeFilipkin/pulsemixer/master/pulsemixer > ./pulsemixer && chmod +x ./pulsemixer
  configure_pulseaudio
}

configure_pulseaudio () {
  sudo cp etc/pulse/client.conf /etc/pulse/client.conf
  sudo cp etc/pulse/daemon.conf /etc/pulse/daemon.conf
  sudo cp etc/pulse/default.pa /etc/pulse/default.pa
  sudo cp etc/pulse/system.pa /etc/pulse/system.pa
  sudo cp etc/systemd/system/pulseaudio.service /etc/systemd/system/pulseaudio.service
  sudo chown root:root /etc/systemd/system/pulseaudio.service
  sudo cp etc/alsa/conf.d/99-pulseaudio.conf /etc/alsa/conf.d/99-pulseaudio.conf
  sudo chown root:root /etc/alsa/conf.d/99-pulseaudio.conf
  sudo systemctl enable --now pulseaudio.service
  sudo systemctl --global mask pulseaudio.socket
}

install_bluetooth () {
  sudo apt install -y --no-install-recommends bluez-tools pulseaudio-module-bluetooth
  sudo usermod -a -G bluetooth pulse
  configure_bluetooth
}

configure_bluetooth () {
  sudo cp etc/bluetooth/main.conf /etc/bluetooth/main.conf
  sudo mkdir -p /etc/systemd/system/bthelper@.service.d
  sudo cp etc/systemd/system/bthelper@.service.d/override.conf /etc/systemd/system/bthelper@.service.d/override.conf
  sudo chown root:root /etc/systemd/system/bthelper@.service.d/override.conf
  sudo cp etc/systemd/system/bt-agent@.service /etc/systemd/system/bt-agent@.service
  sudo chown root:root /etc/systemd/system/bt-agent@.service
  systemctl daemon-reload
  systemctl enable bt-agent@hci0.service
}

install_mpd () {
  sudo apt install -o Dpkg::Options::="--force-confold" -y mpd
  sudo apt install -y mpc
  sudo usermod -a -G pulse-access mpd
  configure_mpd
}

configure_mpd () {
  sudo cp etc/mpd.conf /etc/mpd.conf
  sudo cp etc/systemd/system/mpd.service /etc/systemd/system/mpd.service
  sudo chown root:root /etc/systemd/system/mpd.service
  sudo systemctl daemon-reload
  sudo systemctl enable mpd
  sudo systemctl start mpd
  sudo cp etc/cron.d/rp_crontab /etc/cron.d/rp_crontab
  sudo chown root:root /etc/cron.d/rp_crontab
  sudo systemctl restart cron
  sudo cp src/radio.mpl.m3u /var/lib/mpd/playlists/radio.mpl.m3u
  sudo chown mpd:audio /var/lib/mpd/playlists/radio.mpl.m3u
}

configure_gpiod () {
  sudo cp etc/systemd/system/gpiod.service /etc/systemd/system/gpiod.service
  sudo chown root:root /etc/systemd/system/gpiod.service
  sudo systemctl daemon-reload
  sudo systemctl enable gpiod
  sudo systemctl start gpiod
}

install_spotifyd () {
  wget https://github.com/Spotifyd/spotifyd/releases/download/v0.3.3/spotifyd-linux-armv6-slim.tar.gz -O work/spotifyd-linux-armv6-slim.tar.gz
  tar -xzvf work/spotifyd-linux-armv6-slim.tar.gz work/
  chmod 755 work/spotifyd
  configure_spotifyd
}

configure_spotifyd () {
  mkdir -p /home/pi/.config/spotifyd
  if [ ! -f /home/pi/.config/spotifyd/spotifyd.conf ]; then
    cp src/spotifyd.conf /home/pi/.config/spotifyd/spotifyd.conf
    echo "WARNING: Udate username and password in /home/pi/.config/spotifyd/spotifyd.conf"
  fi
  sudo cp etc/systemd/system/spotifyd.service /etc/systemd/system/spotifyd.service
  sudo chown root:root /etc/systemd/system/spotifyd.service
  sudo systemctl daemon-reload
  sudo systemctl enable spotifyd
  sudo systemctl start spotifyd
}

configure_httpd () {
  sudo cp etc/systemd/system/http-server.service /etc/systemd/system/http-server.service
  sudo chown root:root /etc/systemd/system/http-server.service
  cp src/projector.py work/
  cp src/server.py work/
  sudo systemctl daemon-reload
  sudo systemctl enable http-server
  sudo systemctl start http-server
}

install_homeassistant () {
  docker run -d \
    --name homeassistant \
    --privileged \
    --restart=unless-stopped \
    -e TZ=Europe/Warsaw \
    -v /home/pi/raspberry-media-center/homeassistant:/config \
    --network=host \
    ghcr.io/home-assistant/home-assistant:stable
}

diff_config () {
  for f in $( find etc/ -type f ); do
    diff -q ${f} /${f}
  done
}

push_config () {
  for f in $( find etc/ -type f ); do
    sudo cp ${f} /${f}
    sudo chown root:root /${f}
  done
}

pull_config () {
  for f in $( find etc/ -type f ); do
    cp /${f} ${f}
  done
}

print_usage () {
  echo "USAGE: $0 [-a] | [-o <step>]"
}

while getopts ":hao:" arg; do
  case ${arg} in
    a)
      install_base
      configure_network
      sleep 60
      install_pulseaudio
      install_bluetooth
      install_mpd
      configure_gpiod
      install_spotifyd
      configure_httpd
      install_homeassistant
      ;;
    o)
      f=$OPTARG
      $f
      ;;
    h | *)
      print_usage
      ;;
  esac
done

