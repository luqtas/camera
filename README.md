# camera
a digital waist-level finder camera with Pi's Global Shutter!

# wiring
screen,
PIN 2 - 5V
PIN 6 - GND
PIN 11 - TP_IRQ
PIN 13 - RST
PIN 15 - LCD_RS
PIN 19 - LCD_SI/TP_SI
PIN 21 - TP_SO
PIN 23 - LCD_SCK/TP_SCK
PIN 24 - LCD_CS
PIN 26 - TP_CS
hi guys, can you hear me? (microphone)
PIN 9 - GND
PIN 1 - VDD
PIN 12 - SCK
PIN 35 - WS
PIN 38 - SD
for the buttons, we have a commented function for returning their GPIO,
PIN 14 - GND
PIN 5 - BTN1 (GPIO3)
PIN 37 - BTN2 (GPIO26)
PIN 33 - BTN3 (GPIO13) 
PIN 31 - BTN4 (GPIO6) 
PIN 29 - BTN5 (GPIO5)
PIN 27 - BTN6 (GPIO0)
PIN 40 - BTN7 (GPIO21)
PIN 32 - BTN8 (GPIO12)
PIN 28 - BTN9 (GPIO1)

# after installing Bullseye on your Pi Zero 2W,
keep in mind we are using user name as "dwlfc", gotta update this script to accept $USER...

sudo apt update
sudo apt upgrade
sudo apt install python3-opencv unclutter

cd Downloads
git clone https://github.com/goodtft/LCD-show.git
chmod -R 755 LCD-show
cd LCD-show
sudo ./LCD24-3A+-show

sudo nano /etc/xdg/openbox/lxde-pi-rc.xml
then we need to find <applications> and add these lines
<application name="dwlfc">
<decor>no</decor>
</application>

right click at the panel
Panel Settings > Advanced
check "Minimise panel when not in use"

we also need to parse the service.file into /lib/systemd/sytem
sudo mv dwlfc.service /lib/systemd/system/
sudo nano /lib/systemd/system/dwlfc.service
sudo systemctl daemon-reload
sudo systemctl enable dwlfc.service
we also need hdmi.sh and lcd.sh at /home/user/Downloads
cd Downloads
chmod -R 755 hdmi.sh
chmod -R 755 lcd.sh
reboot