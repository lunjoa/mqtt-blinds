from time import sleep
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import os

MQTT_SERVER = os.environ.get('MQTT_SERVER')
MQTT_PATH = "home-assistant/cover/#"
MQTT_PORT = os.environ.get('MQTT_PORT')
UP_BUTTON_PIN = 6
DOWN_BUTTON_PIN = 13
SELECT_BUTTON_PIN = 5
MY_BUTTON_PIN = 19
KITCHEN_LED_PIN = 25
EAST_LED_PIN = 7
SOUTH_LED_PIN = 8
WEST_LED_PIN = 1
BUTTON_DELAY = 0.15


class Cover:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(UP_BUTTON_PIN, GPIO.OUT)
        GPIO.setup(DOWN_BUTTON_PIN, GPIO.OUT)
        GPIO.setup(SELECT_BUTTON_PIN, GPIO.OUT)
        GPIO.setup(MY_BUTTON_PIN, GPIO.OUT)
        GPIO.setup(KITCHEN_LED_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(EAST_LED_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(SOUTH_LED_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(WEST_LED_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.current_cover= ""
        self.selectButton()
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(os.environ.get('MQTT_USER', os.environ.get('MQTT_PASSWORD'))
        self.client.connect(MQTT_SERVER, MQTT_PORT, 60)
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        self.client.subscribe(MQTT_PATH)

    def on_message(self, client, userdata, msg):
        print(msg.topic + " PAYLOAD: " + str(msg.payload))
        topic_string = str(msg.topic)
        topic = topic_string.split("/")
        cover = topic[2]
        print(cover)
        if msg.payload == "OPEN":
            print("open")
            self.up(cover)
        elif msg.payload == "CLOSE":
            print("close")
            self.down(cover)
        elif msg.payload == "STOP":
            print("stop")
            self.stop(cover)

    def pressButton(self, button_pin):
        print("Pressing button " + str(button_pin))
        GPIO.output(button_pin, 1)
        sleep(BUTTON_DELAY)
        GPIO.output(button_pin, 0)
        sleep(BUTTON_DELAY)

    def selectButton(self):
        self.pressButton(SELECT_BUTTON_PIN)
        print("KITCHEN, EAST, SOUTH, WEST: " + str(GPIO.input(KITCHEN_LED_PIN)) + str(GPIO.input(EAST_LED_PIN)) + str(GPIO.input(SOUTH_LED_PIN)) + str(GPIO.input(WEST_LED_PIN)))
        if not GPIO.input(KITCHEN_LED_PIN) and not GPIO.input(EAST_LED_PIN) and not GPIO.input(SOUTH_LED_PIN) and not GPIO.input(WEST_LED_PIN):
            self.current_cover = "ALL"
        elif not GPIO.input(KITCHEN_LED_PIN):
            self.current_cover = "KITCHEN"
        elif not GPIO.input(EAST_LED_PIN):
            self.current_cover = "EAST"
        elif not GPIO.input(SOUTH_LED_PIN):
            self.current_cover = "SOUTH"
        elif not GPIO.input(WEST_LED_PIN):
            self.current_cover = "WEST"
        print("Selecting cover, current cover: " + self.current_cover)

    def selectCover(self, cover_to_select):
        print("Selecting cover " + cover_to_select)
        if self.current_cover != cover_to_select:
            self.pressButton(SELECT_BUTTON_PIN)
            while True:
                if self.current_cover == cover_to_select:
                    print("break")
                    break
                print("else")
                self.selectButton()

    def up(self, cover):
        print("Making cover go up: " + cover)
        self.selectCover(cover)
        self.pressButton(UP_BUTTON_PIN)

    def down(self, cover):
        print("Making cover go down: " + cover)
        self.selectCover(cover)
        self.pressButton(DOWN_BUTTON_PIN)

    def stop(self, cover):
        print("Making cover stop: " + cover)
        self.selectCover(cover)
        self.pressButton(MY_BUTTON_PIN)


cover = Cover()
