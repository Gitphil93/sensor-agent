# Beatmap Sensor Setup

This sensor runs on a Raspberry Pi Zero 2 W with an INMP441 I2S microphone. It records short audio samples, preprocesses them, and runs automatically on boot with `systemd`.

## Hardware

Tested setup:
- Raspberry Pi Zero 2 W
- INMP441 I2S MEMS microphone

### Working wiring

Pi -> INMP441

- Pin 1 (3.3V) -> VDD
- Pin 6 (GND) -> GND
- Pin 12 (GPIO18) -> SCK
- Pin 35 (GPIO19) -> WS
- Pin 38 (GPIO20) -> SD
- Pin 39 (GND) -> L/R

Notes:
- Use **3.3V**, never 5V
- `L/R -> GND` puts audio on the **left channel**


## Raspberry Zero 2W config

Edit:

```bash
sudo nano /boot/firmware/config.txt
```

# Make sure this is present:
dtparam=i2s=on

[all]
dtoverlay=googlevoicehat-soundcard

# reboot after changing config

```bash 
sudo reboot
````


# Verify audio device

## After reboot:

```bash arecord -l```


#Use the correct device when recording:

```bash arecord -D plughw:1,0 -f S32_LE -r 48000 -c 2 -d 5 test.wav```


#Working processing command:

```bash sox input.wav output.wav remix 1 gain -n```


#example .env:

SENSOR_ID=beatmap-01
API_BASE_URL=https://your-api.example.com
API_TOKEN=change-me
ARECORD_DEVICE=plughw:1,0
RECORD_SECONDS=10
INTERVAL_SECONDS=60
OUTPUT_DIR=/home/username/sensor-agent/sensor/recordings


#Run manually

##From the sensor folder:

python3 main.py
Run automatically on boot

Create the systemd service:

sudo nano /etc/systemd/system/beatmap-sensor.service

##Example:

[Unit]
Description=Beatmap Sensor Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=username
WorkingDirectory=/home/username/sensor-agent/sensor
EnvironmentFile=/home/username/sensor-agent/sensor/.env
ExecStart=/usr/bin/python3 /home/philip/sensor-agent/sensor/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

#Then enable and start it:

sudo systemctl daemon-reload
sudo systemctl enable beatmap-sensor.service
sudo systemctl start beatmap-sensor.service
View logs
journalctl -u beatmap-sensor.service -f

#When code changes

##After pushing changes to GitHub, update the sensor like this:

```bash cd ~/sensor-agent
git pull
sudo systemctl restart beatmap-sensor.service```

##If you changed the systemd service file, also run:

```bash sudo systemctl daemon-reload
sudo systemctl restart beatmap-sensor.service```

