# Raspberry Media Center
Raspberry Pi based home media center

## Overview

Media center is based on:
- Raspberry Pi 4B with 8G RAM
- HiFiBerry DAC2 Pro - [documentation](https://www.hifiberry.com/shop/boards/hifiberry-dac2-pro/)
- 3x Busch und Jaeger 8212u and 1x8211u amplifiers - [documentation](https://library.e.abb.com/public/dec74a007bb7476d8d56ac41941bf79a/8211_ABB_OA_2012-12-17_PL_R01.pdf)
- Case from Busch und Jaeger 8201 Zentralle

![layout](images/layout.jpg)

### Bus connectivity

The system connectivity:
![system](images/system.png)


The RJ45 should be connected as below - consult bus color scheme:

![plugscheme](images/plugscheme.png)

| PIN | COLOR  | PURPOSE | Comment |
|-----|--------|---------|---------|
| 7   | Gray   | (-)     | GND     |
| 1   | Violet | D       | PROG    |
| 2   | Blue   | A       | CALL    |
| 6   | Green  | R1      | AUX     |
| 5   | Yellow | L1      | AUX     |
| 4   | Orange | R2      | FM      |
| 3   | Red    | L2      | FM      |
| 8   | Brown  | (+)     | VCC     |



Comments
- AUX commected to HiFiBerry
- FM connetected to internal Raspberry sound card and headphones output. This results in rather low output level and low quality. Potential improvement is to use pre-amplifier. 
- D pin is used by the external amplifiers to send PROG signal to change the current playing radio station. This is via voltage divider (10k/18kOhm) to GPIO27


## Software

Following software is uesd:
- Raspian 10
- [MPD](https://www.musicpd.org/) for playing internet radio over FM channel. 
- custom daemon to handle GPIO
- [spotifyd](https://spotifyd.github.io/spotifyd/Introduction.html)

### Playback devices available
To list use `aplay -l`:
```
**** List of PLAYBACK Hardware Devices ****
card 0: Headphones [bcm2835 Headphones], device 0: bcm2835 Headphones [bcm2835 Headphones]
  Subdevices: 7/8
  Subdevice #0: subdevice #0
  Subdevice #1: subdevice #1
  Subdevice #2: subdevice #2
  Subdevice #3: subdevice #3
  Subdevice #4: subdevice #4
  Subdevice #5: subdevice #5
  Subdevice #6: subdevice #6
  Subdevice #7: subdevice #7
card 1: sndrpihifiberry [snd_rpi_hifiberry_dacplus], device 0: HiFiBerry DAC+ Pro HiFi pcm512x-hifi-0 [HiFiBerry DAC+ Pro HiFi pcm512x-hifi-0]
  Subdevices: 1/1
  Subdevice #0: subdevice #0

```

### MPD 
Mostly default, except the audio sink to the 
```
audio_output {
	type		    "alsa"
	name		    "My ALSA Device"
	device		    "hw:0,0"	# optional
	mixer_type      "hardware"  # optional
	mixer_device	"default"	# optional
	mixer_control	"PCM"		# optional
	mixer_index	    "0"	        # optional
}

```

Listing playlists
```
pi@raspberrypi:~ $ mpc lsplaylists
radio.mpl
pi@raspberrypi:~ $ mpc playlist
Radio Nowy Swiat: Kłusem z Bluesem - Randka w ciemno
https://stream.rcs.revma.com/an1ugyygzk8uv
```

Make sure that shuffle is enabled: `mpc shuffle`

Adding radio station to list:
```
mpc add <url>
```

Changing radio station (to make sure the list is looped):
```
mpc next;mpc play
```

### GPIO daemon
- consider using [pigpio](https://abyz.me.uk/rpi/pigpio/pigpiod.html)

Daemon config file: `/etc/systemd/system/gpiod.service`
Install:
```
cp src/gpio-listener.py ~pi/
sudo cp src/gpiod.service /etc/systemd/system/gpiod.service
sudo systemctl enable gpiod
```
