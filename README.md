# Requirements

## OS
* Raspbian
* __**Enable i2c under Interfacing Options**__: `sudo raspi-config`

## pre-requisite packages/modules
`sudo apt install python-setuptools python3-setuptools python-smbus python3-smbus python-dev python3-dev`

## pigpio:
* http://abyz.me.uk/rpi/pigpio/download.html
```
wget https://github.com/joan2937/pigpio/archive/master.zip
unzip master.zip
cd pigpio-master
make
sudo make install
```

## picon Zero:
* http://4tronix.co.uk/blog/?p=1224
```
wget http://4tronix.co.uk/piconz.sh -O piconz.sh
bash piconz.sh
```

## pigpiod As a Service
`sudo nano /etc/systemd/system/syspgiod.service`
```[Unit]
Description=PiGPIO Daemon
After=network.target syslog.target
StartLimitIntervalSec=60
StartLimitBurst=5
StartLimitAction=reboot

[Service]
Type=simple
ExecStartPre=/sbin/sysctl -w net.ipv4.tcp_keepalive_time=300
ExecStartPre=/sbin/sysctl -w net.ipv4.tcp_keepalive_intvl=60
ExecStartPre=/sbin/sysctl -w net.ipv4.tcp_keepalive_probes=5
# Don't fork pigpiod
ExecStart=/usr/local/bin/pigpiod -g
ExecStop=
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target```

```sudo chmod 644 /etc/systemd/system/syspgiod.service
sudo systemd-analyze verify syspgiod.service
sudo systemctl daemon-reload
sudo systemctl enable syspgiod.service
sudo systemctl start syspgiod.service```

## After Install
* Reboot for i2c to take effect.
`sudo reboot`

# Notes
* Only tested on Raspberry Pi Zero W (Linux edison 4.19.97+ #1294 Thu Jan 30 13:10:54 GMT 2020 armv6l GNU/Linux)
* Do not forget to turn off your tx after using it.

# Todo
* Implement Blinkt!
* Make a hammer attached to a servo swinging at high speeds/torque an option.
* Webcam attached to RC?
* Deploy fireworks?
* Speaker system with raspotify and 4g hat?
* GPS module for war... RCing?
* Turn signals and night lamps.
* Option for flight
* Easter eggs in code
* Autonomy at unexpected times

# Problems in dev
* Token signals on interval to every 250ms and only setOutput every 250ms
