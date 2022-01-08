# domoticz-AirHumidifier2
Domoticz plugin for Xiaomi Humidifier 1 and 2
* based on https://github.com/mgrom/domoticz-AirHumidifier

* FIX! Work on windows and linux devices
* Add Russian translation
* Add Waterlevel sensor
* Add select model list
  * zhimi.humidifier.v1
  * zhimi.humidifier.ca1
  * zhimi.humidifier.cb1
  * zhimi.humidifier.cb2
  * zhimi.humidifier.ca4 (mb work)
* Add fix value level, if waterlevel sensor broken - 87%=Max and 32%=Min (>_<)
* Work with latest python-miio-0.5.9.2 (at this moment, **0.5.4 - unsupported, mb.**)

TODO:
* Add mathematic fix value level (available in dev-5 branch)
## Installation
```
sudo pip3 install -U python-miio
```
* Make sure your Domoticz instance supports Domoticz Plugin System - see more https://www.domoticz.com/wiki/Using_Python_plugins

* Get plugin data into DOMOTICZ/plugins directory
```
cd YOUR_DOMOTICZ_PATH/plugins
git clone https://github.com/develop-dvs/domoticz-AirHumidifier2
```
Restart Domoticz
* Go to Setup > Hardware and create new Hardware with type: AirHumidifier2
* Enter name (it's up to you), user name and password if define. If not leave it blank
* Select your model (zhimi.humidifier.v1 / ... / zhimi.humidifier.ca4)

## Update
```
sudo pip3 install -U python-miio --upgrade
cd YOUR_DOMOTICZ_PATH/plugins/domoticz-AirHumidifier2
git pull
```
* Restart Domoticz

## Troubleshooting

In case of issues, mostly plugin not visible on plugin list, check logs if plugin system is working correctly. See Domoticz wiki for resolution of most typical installation issues http://www.domoticz.com/wiki/Linux#Problems_locating_Python
