from machine import Pin, ADC
from time import sleep
import dht
from umqtt.simple import MQTTClient
import random

# Konfigurasi koneksi Wi-Fi
WIFI_SSID = 'PCU_Sistem_Kontrol'
WIFI_PASSWORD = 'lasikonn'

# Konfigurasi broker MQTT
MQTT_SERVER = '192.168.41.73'
MQTT_PORT = 1883
DHT_TOPIC = b'4173/dht'
POT_TOPIC = b'4173/potensio'
DUMMY_TOPIC = b'4173/dummy'

# Fungsi untuk menghubungkan ke Wi-Fi
def connect_to_wifi():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Menghubungkan ke Wi-Fi...')
        sta_if.active(True)
        sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
        while not sta_if.isconnected():
            pass
    print('Terhubung ke Wi-Fi:', sta_if.ifconfig()[0])

# Fungsi untuk mengirim data ke broker MQTT
def publish_data(topic, data):
    client = MQTTClient('esp8266', MQTT_SERVER, port=MQTT_PORT)
    client.connect()
    client.publish(topic, str(data))  # Mengonversi data menjadi string sebelum dikirim
    client.disconnect()

# Koneksi ke Wi-Fi
connect_to_wifi()

# Inisialisasi sensor
pot = ADC(0)
sensor = dht.DHT11(Pin(14))

# Variabel untuk penambahan dan pengurangan bilangan
value = 1
increment = True

while True:
    # Membaca nilai dari potensiometer
    pot_value = pot.read()
    pot_value_mapped = int(((pot_value - 3) * 250) / 1021)
    print('Kecepatan: ' + str(pot_value_mapped) + ' Km/H')
    sleep(0.1)
    
    try:
        sleep(2)
        # Membaca nilai suhu dari sensor DHT11
        sensor.measure()
        temp = sensor.temperature()
        print('Temperature: %3.1f C' % temp)
        
        # Mengirimkan data ke broker MQTT
        dht_data = temp
        publish_data(DHT_TOPIC, dht_data)
        
        pot_data = pot_value_mapped
        publish_data(POT_TOPIC, pot_data)
        
        if pot_value == 3:
            # Mengecek jika nilai mencapai batas atas (3)
            # dan melakukan penjumlahan dan pengurangan pada dummy
            if increment:
                value += 1
                if value >= 3:
                    increment = False
            else:
                value -= 1
                if value <= 1:
                    increment = True
        
        dummy_data = value
        publish_data(DUMMY_TOPIC, dummy_data)
        
        print('Penumpang: ' + str(value))
        
    except OSError as e:
        print('Failed to read sensor.')



