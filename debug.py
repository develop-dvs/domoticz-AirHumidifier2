import miio.airhumidifier
import miio.airhumidifier_miot

MyHumidifier = miio.airhumidifier.AirHumidifier("192.168.1.124", "22be42754b31ac440d6394254b38f71c")
data = MyHumidifier.status()
print(data)