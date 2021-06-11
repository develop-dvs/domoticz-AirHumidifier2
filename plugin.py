# A Python plugin for Domoticz to access AirHumidifier2
#
# Author: DCRM
#
# TODO: ??
#
# v 0.3
"""
<plugin key="AirHumidifier2" name="Xiaomi Air Humidifier" author="DCRM" version="0.3" wikilink="https://github.com/rytilahti/python-miio" externallink="https://github.com/develop-dvs/domoticz-AirHumidifier2">
    <params>
		<param field="Address" label="IP Address" width="200px" required="true" default="127.0.0.1"/>
		<param field="Mode1" label="AirHumidifier Token" default="" width="400px" required="true"  />
		<param field="Mode2" label="Model" width="160px">
			<options>
				<option label="zhimi.humidifier.v1" value="zhimi.humidifier.v1" default="true"/>
				<option label="zhimi.humidifier.ca1" value="zhimi.humidifier.ca1"/>
				<option label="zhimi.humidifier.cb1" value="zhimi.humidifier.cb1"/>
                <option label="zhimi.humidifier.ca4 (mb work)" value="zhimi.humidifier.ca4"/>
			</options>
		</param>
        <param field="Mode3" label="Check every x minutes" width="40px" default="15" required="true" />
        <param field="Mode4" label="Water limit turn off level" width="40px" default="15" />
		<param field="Mode6" label="Debug" width="75px">
			<options>
				<option label="True" value="Debug"/>
				<option label="False" value="Normal" default="true" />
			</options>
		</param>
    </params>
</plugin>
"""
import Domoticz
import sys
import datetime
import socket
import subprocess
# Python framework in Domoticz do not include OS dependent path
#
from pathlib import Path

import miio.airhumidifier
import miio.airhumidifier_miot

L10N = {
    'ru': {
        "Humidity":
            "Влажность",
        "Target Humidity":
            "Целевая влажность",
        "Temperature":
            "Температура",
        "Fan Speed":
            "Скорость",
        "Power":
            "Питание",
        "Source":
            "Режим работы",
        "Target":
            "Цель",
        "Water level":
            "Уровень воды",
        "Normal waterlevel":
            "Достаточно воды",
        "Mini waterlevel":
            "Мало воды",
        "Auto|Silent|Medium|High":
            "Авто|Тихий|Нормальный|Максимальный",
        "Favorite Fan Level":
            "Выбранная скорость",
        "Device Unit=%(Unit)d; Name='%(Name)s' already exists":
            "Устройство Unit=%(Unit)d; Name='%(Name)s' уже существует",
        "Creating device Name=%(Name)s; Unit=%(Unit)d; ; TypeName=%(TypeName)s; Used=%(Used)d":
            "Добавление устройства Name=%(Name)s; Unit=%(Unit)d; ; TypeName=%(TypeName)s; Used=%(Used)d",
        "%(Vendor)s - %(Address)s, %(Locality)s<br/>Station founder: %(sensorFounder)s":
            "%(Vendor)s - %(Address)s, %(Locality)s<br/>Местоположение устройства: %(sensorFounder)s",
        "%(Vendor)s - %(Locality)s %(StreetNumber)s<br/>Station founder: %(sensorFounder)s":
            "%(Vendor)s - %(Locality)s %(StreetNumber)s<br/>Местоположение устройства: %(sensorFounder)s",
        "Great humidity":
            "Очень влажно",
        "Good humidity":
            "Хорошая влажность",
        "Poor humidity":
            "Суховато",
        "Bad humidity":
            "Очень сухо",
        "Sensor id (%(sensor_id)d) not exists":
            "Сенсор (%(sensor_id)d) не существует",
        "Not authorized":
            "Не авторизован",
        "Starting device update":
            "Запущено обновление устройств",
        "Update unit=%d; nValue=%d; sValue=%s":
            "Обновлено unit=%d; nValue=%d; sValue=%s",
        "Awaiting next pool: %s":
            "Ожидание запроса в: %s",
        "Next pool attempt at: %s":
            "Следующий запрос в: %s",
        "Unrecognized error: %s":
            "Ошибка: %s"
    },
    'pl': {
        "Humidity":
            "Wilgotność",
        "Target Humidity":
            "Docelowa wilgotność",
        "Temperature":
            "Temperatura",
        "Fan Speed":
            "Prędkość wiatraka",
        "Favorite Fan Level":
            "Ulubiona prędkość wiatraka",
        "Device Unit=%(Unit)d; Name='%(Name)s' already exists":
            "Urządzenie Unit=%(Unit)d; Name='%(Name)s' już istnieje",
        "Creating device Name=%(Name)s; Unit=%(Unit)d; ; TypeName=%(TypeName)s; Used=%(Used)d":
            "Tworzę urządzenie Name=%(Name)s; Unit=%(Unit)d; ; TypeName=%(TypeName)s; Used=%(Used)d",
        "%(Vendor)s - %(Address)s, %(Locality)s<br/>Station founder: %(sensorFounder)s":
            "%(Vendor)s - %(Address)s, %(Locality)s<br/>Sponsor stacji: %(sensorFounder)s",
        "%(Vendor)s - %(Locality)s %(StreetNumber)s<br/>Station founder: %(sensorFounder)s":
            "%(Vendor)s - %(Locality)s %(StreetNumber)s<br/>Sponsor stacji: %(sensorFounder)s",
        "Great humidity":
            "Bardzo dobra wilgotność",
        "Good humidity":
            "Dobra wilgotność",
        "Poor humidity":
            "Przeciętna wilgotność",
        "Bad humidity":
            "Zła wilgotność",
        "Sensor id (%(sensor_id)d) not exists":
            "Sensor (%(sensor_id)d) nie istnieje",
        "Not authorized":
            "Brak autoryzacji",
        "Starting device update":
            "Rozpoczynanie aktualizacji urządzeń",
        "Update unit=%d; nValue=%d; sValue=%s":
            "Aktualizacja unit=%d; nValue=%d; sValue=%s",
        "Awaiting next pool: %s":
            "Oczekiwanie na następne pobranie: %s",
        "Next pool attempt at: %s":
            "Następna próba pobrania: %s",
        "Unrecognized error: %s":
            "Nierozpoznany błąd: %s"
    },
    'en': { }
}

def _(key):
    try:
        return L10N[Settings["Language"]][key]
    except KeyError:
        return key
    
def humiExecute(AddressIP, token, model):
    """New model https://python-miio.readthedocs.io/en/latest/api/miio.airhumidifier_miot.html"""

    if model == 'zhimi.humidifier.ca4':
        return miio.airhumidifier_miot.AirHumidifierMiot(AddressIP, token)
    else:
        return miio.airhumidifier.AirHumidifier(AddressIP, token, 0, 0, True, model)

class UnauthorizedException(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class SensorNotFoundException(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class ConnectionErrorException(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

# temporery class

class HumidifierStatus:
    """Container for status reports from the air humidifier."""

    def __init__(self, AddressIP, token, model):
        """
        Response of script: V1
               "<AirHumidifierStatus power=on, humidity=36%," \
               "mode=OperationMode.Silent,led=True,led_brightness=LedBrightness.Bright,buzzer=False, " \
               "child_lock=False, " \
               "use_time=3748042> "
               
        Response of script: V2
        <AirHumidiferStatus power=on, mode=OperationMode.High, temperature=24.6, humidity=50%,
        led_brightness=LedBrightness.Off, buzzer=False, child_lock=False, target_humidity=70%,
        trans_level=None, motor_speed=996, depth=87, dry=False, use_time=0000002, hardware_version=0001,
        button_pressed=None, strong_mode_enabled=False, firmware_version_major=1.6.7, firmware_version_minor=0>
        
        """

        addressIP = str(AddressIP)
        token = str(token)
        model = str(model)
        MyHumidifier = humiExecute(AddressIP, token, model)

        data = MyHumidifier.status()
        if model == 'zhimi.humidifier.ca4':
            if Parameters["Mode6"] == 'Debug':
                Domoticz.Debug(str(data))
            self.power = data.power
            self.humidity = data.humidity
            self.temperature = data.temperature
            self.mode = data.mode
            self.target_humidity = data.target_humidity
            self.waterlevel = data.water_level
            self.dry = data.dry
            self.led_brightness = data.led_brightness
            self.motor_speed = data.motor_speed
            return

        data = str(data)
        if Parameters["Mode6"] == 'Debug':
            Domoticz.Debug(data[:30] + " .... " + data[-30:])
        data = data[19:-2]
        data = data.replace(' ', '')
        data = dict(item.split("=") for item in data.split(","))
        self.power = data["power"]
        self.humidity = int(data["humidity"][:-1])
        self.temperature = data["temperature"]
        self.mode = data["mode"]
        self.target_humidity = int(data["target_humidity"][:-1])
        self.waterlevel=data["depth"]
        for item in data.keys():
            Domoticz.Debug(str(item) + " => " + str(data[item]))

class BasePlugin:
    enabled = False

    def __init__(self):
        # Consts
        self.version = "0.2"

        self.EXCEPTIONS = {
            "SENSOR_NOT_FOUND":     1,
            "UNAUTHORIZED":         2,
        }

        self.debug = False
        self.inProgress = False

        # Do not change below UNIT constants!
        self.UNIT_AIR_QUALITY_INDEX     = 1
        self.UNIT_AIR_POLLUTION_LEVEL   = 2
        self.UNIT_TEMPERATURE           = 3
        self.UNIT_HUMIDITY              = 4
        self.UNIT_MOTOR_SPEED           = 5
        self.UNIT_AVARAGE_AQI           = 6

        self.UNIT_POWER_CONTROL         = 10
        self.UNIT_MODE_CONTROL          = 11
        self.UNIT_MOTOR_SPEED_FAVORITE  = 12

        self.UNIT_TARGET_HUMIDITY       = 13

        self.UNIT_WATER_LEVEL       = 20


        self.nextpoll = datetime.datetime.now()
        return


    def onStart(self):
        Domoticz.Debug("onStart called")
        if Parameters["Mode6"] == 'Debug':
            self.debug = True
            Domoticz.Debugging(1)
            DumpConfigToLog()
        else:
            Domoticz.Debugging(0)

        Domoticz.Heartbeat(20)
        self.pollinterval = int(Parameters["Mode3"]) * 60


        self.variables = {
            self.UNIT_TEMPERATURE: {
                "Name":     _("Temperature"),
                "TypeName": "Temperature",
                "Used":     0,
                "nValue":   0,
                "sValue":   None,
            },
            self.UNIT_HUMIDITY: {
                "Name":     _("Humidity"),
                "TypeName": "Humidity",
                "Used":     0,
                "nValue":   0,
                "sValue":   None,
            },
            self.UNIT_WATER_LEVEL: {
                "Name":     _("Water level"),
                "TypeName": "Percentage",
                "Used":     0,
                "nValue":   0,
                "sValue":   None,
                #"percentage":   0,
            },
            self.UNIT_TARGET_HUMIDITY: {
                "Name":     _("Target Humidity"),
                "TypeName": "Humidity",
                "Used":     0,
                "nValue":   0,
                "sValue":   None,
            }
        }

        #create switches
        if (len(Devices) == 0):
            Domoticz.Device(Name=_("Power"), Unit=self.UNIT_POWER_CONTROL, TypeName="Switch", Image=7).Create()
            Options = {"LevelActions": "||||",
                       "LevelNames": _("Auto|Silent|Medium|High"),
                       "LevelOffHidden": "false",
                       "SelectorStyle": "0"
                      }
            Domoticz.Device(Name=_("Source"), Unit=self.UNIT_MODE_CONTROL, TypeName="Selector Switch", Switchtype=18,
                            Image=7,
                            Options=Options).Create()
            HumidityTarget = {"LevelActions": "|||",
                            "LevelNames": "50%|60%|70%",
                            "LevelOffHidden": "false",
                            "SelectorStyle": "0"}
            Domoticz.Device(Name=_("Target"), Unit=self.UNIT_TARGET_HUMIDITY, TypeName="Selector Switch", Switchtype=18,
                            Image=7,
                            Options=HumidityTarget).Create()
            Domoticz.Log("Devices created.")
        else:
            if (self.UNIT_POWER_CONTROL in Devices ):
                Domoticz.Log("Device UNIT_MODE_CONTROL with id " + str(self.UNIT_POWER_CONTROL) + " exist")
            else:
                Domoticz.Device(Name="Power", Unit=self.UNIT_POWER_CONTROL, TypeName="Switch", Image=7).Create()
            if (self.UNIT_MODE_CONTROL in Devices ):
                Domoticz.Log("Device UNIT_MODE_CONTROL with id " + str(self.UNIT_MODE_CONTROL) + " exist")
            else:
                Options = {"LevelActions": "||||",
                           "LevelNames": _("Auto|Silent|Medium|High"),
                           "LevelOffHidden": "false",
                           "SelectorStyle": "0"
                           }
                Domoticz.Device(Name="Mode", Unit=self.UNIT_MODE_CONTROL, TypeName="Selector Switch", Switchtype=18,
                                Image=7,
                                Options=Options).Create()
            if (self.UNIT_TARGET_HUMIDITY in Devices):
                Domoticz.Log("Device UNIT_TARGET_HUMIDITY with id " + str(self.UNIT_TARGET_HUMIDITY) + " exist")
            else:
                HumidityTarget = {"LevelActions": "|||",
                                "LevelNames": "50%|60%|70%",
                                "LevelOffHidden": "false",
                                "SelectorStyle": "0"}
                Domoticz.Device(Name="Target", Unit=self.UNIT_TARGET_HUMIDITY, TypeName="Selector Switch", Switchtype=18,
                                Image=7,
                                Options=HumidityTarget).Create()                

        self.onHeartbeat(fetch=False)

    def onStop(self):
        Domoticz.Log("onStop called")
        Domoticz.Debugging(0)

    def onConnect(self, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Data, Status, Extra):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log(
            "onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        MyHumidifier = humiExecute(Parameters["Address"], Parameters["Mode1"], Parameters["Mode2"])
        
        if Unit == self.UNIT_POWER_CONTROL and str(Command).upper()=="ON":
            MyHumidifier.on()
        elif Unit == self.UNIT_POWER_CONTROL and str(Command).upper()=="OFF":
            MyHumidifier.off()
        elif Unit == self.UNIT_MODE_CONTROL and int(Level) == 10:
            MyHumidifier.set_mode(miio.airhumidifier.OperationMode.Silent)
        elif Unit == self.UNIT_MODE_CONTROL and int(Level) == 0:
            MyHumidifier.set_mode(miio.airhumidifier.OperationMode.Auto)
        elif Unit == self.UNIT_MODE_CONTROL and int(Level) == 20:
            MyHumidifier.set_mode(miio.airhumidifier.OperationMode.Medium)
        elif Unit == self.UNIT_MODE_CONTROL and int(Level) == 30:
            MyHumidifier.set_mode(miio.airhumidifier.OperationMode.High)
        elif Unit == self.UNIT_TARGET_HUMIDITY and int(Level) == 0:
            MyHumidifier.set_target_humidity(50)
        elif Unit == self.UNIT_TARGET_HUMIDITY and int(Level) == 10:
           MyHumidifier.set_target_humidity(60)
        elif Unit == self.UNIT_TARGET_HUMIDITY and int(Level) == 20:
            MyHumidifier.set_target_humidity(70)
        else:
            Domoticz.Log("onCommand called not found")

        data = str(MyHumidifier.status())
        if Parameters["Mode6"] == 'Debug':
            Domoticz.Debug(data)
        self.onHeartbeat(fetch=True)

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(
            Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self):
        Domoticz.Log("onDisconnect called")

    def postponeNextPool(self, seconds=3600):
        self.nextpoll = (datetime.datetime.now() + datetime.timedelta(seconds=seconds))
        return self.nextpoll

    def createDevice(self, key=None):
        """create Domoticz virtual device"""

        def createSingleDevice(key):
            """inner helper function to handle device creation"""

            item = self.variables[key]
            _unit = key
            _name = item['Name']

            # skip if already exists
            if key in Devices:
                Domoticz.Debug(_("Device Unit=%(Unit)d; Name='%(Name)s' already exists") % {'Unit': key, 'Name': _name})
                return

            try:
                _options = item['Options']
            except KeyError:
                _options = {}

            _typename = item['TypeName']

            try:
                _used = item['Used']
            except KeyError:
                _used = 0

            try:
                _image = item['Image']
            except KeyError:
                _image = 0

            Domoticz.Debug(_("Creating device Name=%(Name)s; Unit=%(Unit)d; ; TypeName=%(TypeName)s; Used=%(Used)d") % {
                               'Name':     _name,
                               'Unit':     _unit,
                               'TypeName': _typename,
                               'Used':     _used,
                           })

            Domoticz.Device(
                Name=_name,
                Unit=_unit,
                TypeName=_typename,
                Image=_image,
                Options=_options,
                Used=_used
            ).Create()

        if key:
            createSingleDevice(key)
        else:
            for k in self.variables.keys():
                createSingleDevice(k)


    def onHeartbeat(self, fetch=False):
        Domoticz.Debug("onHeartbeat called")
        now = datetime.datetime.now()

        if fetch == False:
            if self.inProgress or (now < self.nextpoll):
                Domoticz.Debug(_("Awaiting next pool: %s") % str(self.nextpoll))
                return

        # Set next pool time
        self.postponeNextPool(seconds=self.pollinterval)

        try:
            # check if another thread is not running
            # and time between last fetch has elapsed
            self.inProgress = True

            res = self.sensor_measurement(Parameters["Address"], Parameters["Mode1"], Parameters["Mode2"])

            try:
                self.variables[self.UNIT_HUMIDITY]['sValue'] = str(res.humidity)
            except KeyError:
                pass  # No humidity value

            try:
                humidity = int(round(res.humidity))
                if humidity >= 60 and humidity <= 70:
                    pollutionText = _("Great humidity")
                    humidity_status = 1 # great
                elif (humidity >= 45 and humidity < 60) or (humidity > 70 and humidity <= 80):
                    pollutionText = _("Good humidity")
                    humidity_status = 0 # normal
                elif (humidity >= 30 and humidity < 45) or (humidity > 80):
                    pollutionText = _("Poor humidity")
                    humidity_status = 3 # wet/poor
                elif humidity < 30:
                    pollutionText = _("Bad humidity")
                    humidity_status = 2 # dry

                self.variables[self.UNIT_HUMIDITY]['nValue'] = humidity
                self.variables[self.UNIT_HUMIDITY]['sValue'] = str(humidity_status)
            except KeyError:
                pass  # No humidity value

            try:
                self.variables[self.UNIT_TEMPERATURE]['sValue'] = res.temperature
            except KeyError:
                pass  # No temperature value
            
            try:
                # https://github.com/aholstenson/miio/issues/131#issuecomment-376881949
                # Max depth is 120. That's why value -> value / 1.2.
                waterlevel = (int(res.waterlevel)-14)/1.2

                if waterlevel >= 20:
                    #pollutionText = _("Normal waterlevel")
                    waterlevel_status = 1
                else:
                    #pollutionText = _("Mini waterlevel")
                    waterlevel_status = 0
                
                self.variables[self.UNIT_WATER_LEVEL]['nValue'] = int(waterlevel)
                self.variables[self.UNIT_WATER_LEVEL]['sValue'] = waterlevel
            except KeyError:
                pass  # No water level value
            
            try:
                if res.power == "on":
                    UpdateDevice(self.UNIT_POWER_CONTROL, 1, "AirHumidifier ON")
                elif res.power == "off":
                    UpdateDevice(self.UNIT_POWER_CONTROL, 0, "AirHumidifier OFF")
            except KeyError:
                pass  # No power value

            try:
                if res.mode == "OperationMode.Auto":
                    UpdateDevice(self.UNIT_MODE_CONTROL, 0, '0')
                elif res.mode == "OperationMode.Silent":
                    UpdateDevice(self.UNIT_MODE_CONTROL, 10, '10')
                elif res.mode == "OperationMode.Medium":
                    UpdateDevice(self.UNIT_MODE_CONTROL, 20, '20')
                elif res.mode == "OperationMode.High":
                    UpdateDevice(self.UNIT_MODE_CONTROL, 30, '30')
            except KeyError:
                pass  # No mode value

            try:
                humidity = int(res.target_humidity)
                if humidity == 50:
                    UpdateDevice(self.UNIT_TARGET_HUMIDITY, 0, '0')
                elif humidity == 60:
                    UpdateDevice(self.UNIT_TARGET_HUMIDITY, 10, '10')
                elif humidity == 70:
                    UpdateDevice(self.UNIT_TARGET_HUMIDITY, 20, '20')
            except KeyError:
                pass  # No mode value

            self.doUpdate()
        except Exception as e:
            Domoticz.Error(_("Unrecognized error: %s") % str(e))
        finally:
            self.inProgress = False
        if Parameters["Mode6"] == 'Debug':
            Domoticz.Debug("onHeartbeat finished")
        return True


    def doUpdate(self):
        Domoticz.Log(_("Starting device update"))
        for unit in self.variables:
            nV = self.variables[unit]['nValue']
            sV = self.variables[unit]['sValue']

            # cast float to str
            if isinstance(sV, float):
                sV = str(float("{0:.0f}".format(sV))).replace('.', ',')

            # Create device if required
            if sV:
                self.createDevice(key=unit)
                if unit in Devices:
                    Domoticz.Log(_("Update unit=%d; nValue=%d; sValue=%s") % (unit, nV, sV))
                    Devices[unit].Update(nValue=nV, sValue=sV)

    def sensor_measurement(self, addressIP, token, model):
        """current sensor measurements"""
        return HumidifierStatus(addressIP, token, model)

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Status, Description):
    global _plugin
    _plugin.onConnect(Status, Description)

def onMessage(Data, Status, Extra):
    global _plugin
    _plugin.onMessage(Data, Status, Extra)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect():
    global _plugin
    _plugin.onDisconnect()

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

def UpdateDevice(Unit, nValue, sValue):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it
    if (Unit in Devices):
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue))
            Domoticz.Log("Update " + str(nValue) + ":'" + str(sValue) + "' (" + Devices[Unit].Name + ")")
    return
