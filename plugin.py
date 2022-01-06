# A Python plugin for Domoticz to access AirHumidifier2
#
# Author: DCRM
#
# TODO: ??
#
# v 0.4
"""
<plugin key="AirHumidifier2" name="Xiaomi Air Humidifier" author="DCRM" version="0.4" wikilink="https://github.com/rytilahti/python-miio" externallink="https://github.com/develop-dvs/domoticz-AirHumidifier2">
    <params>
		<param field="Address" label="IP Address" width="200px" required="true" default="127.0.0.1"/>
		<param field="Mode1" label="AirHumidifier Token" default="" width="400px" required="true"  />
		<param field="Mode2" label="Model" width="160px">
			<options>
				<option label="zhimi.humidifier.v1" value="zhimi.humidifier.v1" default="true"/>
				<option label="zhimi.humidifier.ca1" value="zhimi.humidifier.ca1"/>
				<option label="zhimi.humidifier.cb1" value="zhimi.humidifier.cb1"/>
				<option label="zhimi.humidifier.cb2" value="zhimi.humidifier.cb2"/>
                <option label="zhimi.humidifier.ca4" value="zhimi.humidifier.ca4"/>
			</options>
		</param>
        <param field="Mode3" label="Check every x minutes" width="40px" default="15" required="true" />
        <param field="Mode4" label="Water level FORCE MIN value" width="40px" default="0" />
        <param field="Mode5" label="Water limit FORCE MAX value" width="40px" default="100" />
		<param field="Mode6" label="Debug" width="75px">
			<options>
				<option label="True" value="Debug"/>
				<option label="False" value="Normal" default="true" />
			</options>
		</param>
    </params>
</plugin>
"""
import datetime

import Domoticz
import miio.airhumidifier
import miio.airhumidifier_miot

# Python framework in Domoticz do not include OS dependent path
#

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
    'en': {}
}


def _(key):
    try:
        return L10N[Settings["Language"]][key]
    except KeyError:
        return key


def humiExecute(ip, token, model):
    """New model https://python-miio.readthedocs.io/en/latest/api/miio.airhumidifier_miot.html"""
    if model == miio.airhumidifier_miot.SMARTMI_EVAPORATIVE_HUMIDIFIER_2:  # "zhimi.humidifier.ca4"
        return miio.airhumidifier_miot.AirHumidifierMiot(ip, token)
    else:
        return miio.airhumidifier.AirHumidifier(ip, token)


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


class HumidifierStatus:
    """Container for status reports from the air humidifier."""

    def __init__(self, ip, token, model):
        """
        Response of script:
        <AirHumidifierStatus button_pressed=None buzzer=False child_lock=False depth=84 dry=False
         firmware_version=2.1.0 firmware_version_major=2.1.0 firmware_version_minor=0
         hardware_version=0001 humidity=60 is_on=True led_brightness=LedBrightness.Off
          mode=OperationMode.High motor_speed=996 power=on strong_mode_enabled=False target_humidity=70
          temperature=25.9 trans_level=None use_time=29265406 water_level=70 water_tank_detached=False>
        """
        Domoticz.Debug("HumidifierStatus __init__ start")

        token = str(token)
        model = str(model)
        humiRef = humiExecute(ip, token, model)
        data = humiRef.status()

        if Parameters["Mode6"] == 'Debug':
            Domoticz.Debug(str(data))

        # Map vars
        self.power = data.power  # str
        self.humidity = data.humidity  # int
        self.temperature = data.temperature  # float
        self.mode = str(data.mode)  # OperationMode enum 0,1,2,3
        self.target_humidity = data.target_humidity  # int
        self.water_level = data.water_level  # int

        if Parameters["Mode6"] == 'Debug':
            Domoticz.Debug("power: " + self.power)
            Domoticz.Debug("humidity: " + str(self.humidity))
            Domoticz.Debug("temperature: " + str(self.temperature))
            Domoticz.Debug("mode: " + self.mode)
            Domoticz.Debug("target_humidity: " + str(self.target_humidity))
            Domoticz.Debug("water_level: " + str(self.water_level))

        # self.dry = data.dry
        # self.led_brightness = data.led_brightness
        # self.motor_speed = data.motor_speed
        return


class BasePlugin:
    enabled = False

    def __init__(self):
        # Consts
        self.version = "0.4"

        self.EXCEPTIONS = {
            "SENSOR_NOT_FOUND": 1,
            "UNAUTHORIZED": 2,
        }

        self.debug = False
        self.inProgress = False

        # Do not change below UNIT constants!
        self.UNIT_AIR_QUALITY_INDEX = 1
        self.UNIT_AIR_POLLUTION_LEVEL = 2
        self.UNIT_TEMPERATURE = 3
        self.UNIT_HUMIDITY = 4
        self.UNIT_MOTOR_SPEED = 5
        self.UNIT_AVARAGE_AQI = 6

        self.UNIT_POWER_CONTROL = 10
        self.UNIT_MODE_CONTROL = 11
        self.UNIT_MOTOR_SPEED_FAVORITE = 12

        self.UNIT_TARGET_HUMIDITY = 13

        self.UNIT_WATER_LEVEL = 20

        self.nextpoll = datetime.datetime.now()

        Domoticz.Debug("Miio library:" + ": " + miio.__version__)
        if miio.__version__ == "0.5.4":
            Domoticz.Debug("Please update Miio lib!")

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
                "Name": _("Temperature"),
                "TypeName": "Temperature",
                "Used": 0,
                "nValue": 0,
                "sValue": None,
            },
            self.UNIT_HUMIDITY: {
                "Name": _("Humidity"),
                "TypeName": "Humidity",
                "Used": 0,
                "nValue": 0,
                "sValue": None,
            },
            self.UNIT_WATER_LEVEL: {
                "Name": _("Water level"),
                "TypeName": "Percentage",
                "Used": 0,
                "nValue": 0,
                "sValue": None,
                # "percentage":   0,
            },
            self.UNIT_TARGET_HUMIDITY: {
                "Name": _("Target Humidity"),
                "TypeName": "Humidity",
                "Used": 0,
                "nValue": 0,
                "sValue": None,
            }
        }

        # create switches
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
            if (self.UNIT_POWER_CONTROL in Devices):
                Domoticz.Log("Device UNIT_MODE_CONTROL with id " + str(self.UNIT_POWER_CONTROL) + " exist")
            else:
                Domoticz.Device(Name="Power", Unit=self.UNIT_POWER_CONTROL, TypeName="Switch", Image=7).Create()
            if (self.UNIT_MODE_CONTROL in Devices):
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
                Domoticz.Device(Name="Target", Unit=self.UNIT_TARGET_HUMIDITY, TypeName="Selector Switch",
                                Switchtype=18,
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

        humiRef = humiExecute(Parameters["Address"], Parameters["Mode1"], Parameters["Mode2"])

        try:
            if Unit == self.UNIT_POWER_CONTROL and str(Command).upper() == "ON":
                humiRef.on()
            elif Unit == self.UNIT_POWER_CONTROL and str(Command).upper() == "OFF":
                humiRef.off()
            elif Unit == self.UNIT_MODE_CONTROL and int(Level) == 10:
                humiRef.set_mode(miio.airhumidifier.OperationMode.Silent)
            elif Unit == self.UNIT_MODE_CONTROL and int(Level) == 0:
                humiRef.set_mode(miio.airhumidifier.OperationMode.Auto)
            elif Unit == self.UNIT_MODE_CONTROL and int(Level) == 20:
                humiRef.set_mode(miio.airhumidifier.OperationMode.Medium)
            elif Unit == self.UNIT_MODE_CONTROL and int(Level) == 30:
                humiRef.set_mode(miio.airhumidifier.OperationMode.High)
            elif Unit == self.UNIT_TARGET_HUMIDITY and int(Level) == 0:
                humiRef.set_target_humidity(50)
            elif Unit == self.UNIT_TARGET_HUMIDITY and int(Level) == 10:
                humiRef.set_target_humidity(60)
            elif Unit == self.UNIT_TARGET_HUMIDITY and int(Level) == 20:
                humiRef.set_target_humidity(70)
            else:
                Domoticz.Log("onCommand called not found")
        except Exception as e:
            Domoticz.Error(_("onCommand error: %s") % str(e))

        if Parameters["Mode6"] == 'Debug':
            data = humiRef.status()
            Domoticz.Debug(str(data))

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
                'Name': _name,
                'Unit': _unit,
                'TypeName': _typename,
                'Used': _used,
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
                    humidity_status = 1  # great
                elif (humidity >= 45 and humidity < 60) or (humidity > 70 and humidity <= 80):
                    pollutionText = _("Good humidity")
                    humidity_status = 0  # normal
                elif (humidity >= 30 and humidity < 45) or (humidity > 80):
                    pollutionText = _("Poor humidity")
                    humidity_status = 3  # wet/poor
                elif humidity < 30:
                    pollutionText = _("Bad humidity")
                    humidity_status = 2  # dry

                self.variables[self.UNIT_HUMIDITY]['nValue'] = humidity
                self.variables[self.UNIT_HUMIDITY]['sValue'] = str(humidity_status)
            except KeyError:
                pass  # No humidity value

            try:
                self.variables[self.UNIT_TEMPERATURE]['sValue'] = res.temperature
            except KeyError:
                pass  # No temperature value

            try:
                water_level = int(res.water_level)

                # Force fix water level
                if Parameters["Mode5"] != "":
                    if water_level >= int(Parameters["Mode5"]):
                        water_level = 100
                        # pollutionText = _("Normal water_level")
                        waterlevel_status = 1

                if Parameters["Mode4"] != "":
                    if water_level <= int(Parameters["Mode4"]):
                        water_level = 0
                    # pollutionText = _("Mini water_level")
                    waterlevel_status = 0

                self.variables[self.UNIT_WATER_LEVEL]['nValue'] = int(water_level)
                self.variables[self.UNIT_WATER_LEVEL]['sValue'] = water_level
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

    def sensor_measurement(self, ip, token, model):
        """current sensor measurements"""
        return HumidifierStatus(ip, token, model)


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
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
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
