# About Meccano IoT Project

Meccano project is a multi-purpose IoT (Internet of Things) board and software platform created by Luciano Kadoya, Rogério Biondi, Diego Osse and Talita Paschoini. Its development started in early 2014 as a closed R&D project in the Software Architecture Division, with the aim of creating a board which is robust, based on a modern microprocessor (ESP8266), cheap, easy to implement and deploy through the 750 retail stores to perform several functions, such as:

- Count the number of visitors in each store to calculate the sales/visits ratio;
- Get the vote/feedback of users regarding the services;
- Voice marketing;
- Energy saving initiatives;
- Beacons and interaction of the customer in the physical store;
- Several other undisclosed applications;

Different from other ESP8266 projects, Meccano board has been heavily tested in retail stores and adjusted to be safe against RF (radio frequency) interferences. The physical store is an inhospitable environment since there are several hundreds of electronic products, such as TVs, computers, sound and home theaters as well as electronic home appliances.

The project is still in its early stages and will evolve in the future. Magazine Luiza will plan the backlog and sponsor the project. It has been open-sourced because it´s the first initiative to create a board based on ESP8266 in Brazil and we are really excited with the possibilities. Magazine Luiza has a passion for innovations and contribution to the development of technology. So you are invited to join us because your support/collaboration is welcome!


# Meccano-Raspberry-Pi-Library

Meccano arduino-raspberry-pi-library is a client library for Raspberry Pi.

## Features:

 - Simple to use
 - Seamless Integration to Meccano Gateway    
    - Create and send facts
    - When no connection available, store facts in a local data file.
    - Check and execute messages from gateway

## requirements

In order to use this library, you should have python-2.7 installed.
You may also need to configure and install packages to use the RPI GPIOs. This is beyound the scope of this project, but you may find useful information here:

https://www.raspberrypi.org/blog/using-the-gpio/

https://www.raspberrypi.org/documentation/usage/gpio/

http://makezine.com/projects/tutorial-raspberry-pi-gpio-pins-and-python/


## Installation

- Install python

```
apt-get install -y python*
```

- Install the meccano client Library

Download it from github, from
https://github.com/meccano-iot/raspberry-pi-library

Unzip the package in any directory

- Import and use in your Raspberry Pi programs


### Mininum Meccano Program

You need to include the meccano library in your code:

```
import time
import meccano

# Connect to the server

# For connection you must provide the mac-address of your network adapter,
# The server and port where the meccano gateway is running
if not meccano.setup("66:66:66:66:66:66", "meccano-iot.cyclops.zone", 80):
    print "Could not connect to Meccano Network"
    exit()

# Sending a test fact
fact = meccano.fact_create("teste_yun", 1, 10)
meccano.fact_send(fact, meccano.MODE_PERSISTENT)

# Receiving and processing messages from gateway
while(True):
    custom_messages = meccano.messages_process(30000)
    if len(custom_messages) > 0:
        if "MY_COMMAND" in custom_messages:
            print "Execute my command!"
        print "Custom commands received: "
        print custom_messages
    time.sleep(10)
```

### Ports

You should configure and use your Raspberry Pi GPIOs the same way you're already used to. The code bellow shows the use of RPi package.

```
import RPi.GPIO as GPIO
GPIO.setup(18, GPIO.OUT)
GPIO.output(18, False)
```

### Functions

#### Setup functions ####


##### void led_setup(int gpio); #####

Not available yet.


##### boolean setup(string mac, string server, int port) #####

The setup() will do the following functions:

1. Setup the connection to gateway. You must pass the host (or IP) and port where the meccano gateway is running;
2. It will register the device in the Meccano Network;
3. It will get the clock information.

```
setup("66:66:66:66:66:66", "http://meccano.server.iot", 80)
```


#### Fact functions ####

Facts are the representation of a physical event. They are data captured by the sensors of Meccano Mini Board. It can be a temperature sensor, a line infrared or PIR sensor or others. The data of a fact is represented by a numeric value. Examples: for a temperature sensor it should be a number between -100 and 100 representing the celsius measure, or if you create a button it can be the number of times which it has been pressed by the user.


##### string fact_create(string channel, int sensor, int value) #####

When you create a fact, you must specify a channel. The channel is a class that identify which kind of information you want to send to the meccano gateway. Besides the channel, each fact must specify the sensor. You must define a number for each sensor connected to your Raspberry Pi. Let's consider, for example, that you have a PIR sensor connected in one port and a temperature sensor in other port. for identification, you should consider the PIR as sensor 1 and temperature as sensor 2. If you have several identical appliances which the same configuration, you must keep the same configuration of sensor for all devices. The value of the sensor is the data captured of them. This can be a value of temperature, a voltage or whatever you need to collect.


##### boolean fact_send(string fact, boolean mode); #####

Send a fact to the meccano gateway.
The mode parameter may accept two values:

- ***MODE_PERSISTENT***: if there is no wifi connection available, the data will be persisted to the local database. When there is another data sent to the gateway, if the connection is restablished, local stored data will be sent to the gateway automatically.

- ***MODE_NON_PERSISTENT***: data is discarded if there is no connection.

```
if(GPIO.input(23) == 1):
  print(“Button 1 pressed”)
  String fact = m.fact_create("BUTTON", 1, 1)
  meccano.fact_send(fact, MODE_PERSISTENT);
}
```




#### Data functions ####



##### boolean data_exists() #####

Returns true or false if there is local data stored on device.



##### boolean data_sync() #####

Sends the data stored in the local device manually. The data_sync function is already automatically called in fact_send, but you may also force a synchronization if you need.

```
exists = meccano.data_exists();
if exists:
  print "There is data stored in the device."
  print "Sending to the gateway."
  meccano.data_sync()
```


##### void data_show() #####

Shows the data stored in the local device. This should be used for debug purpose only.

```
if meccano.data_exists():
  meccano.data_show()
```



#### Led and Buzz Functions ####

Not available yet.


##### string[] messages_process(unsigned long elapsed_time) #####

messages_process executes the following functions:

1. Receive messages from Meccano Network/Gateway (such as BLINK and REBOOT) and executes them;
2. Announce device to the gateway;
3. Check if there is local data stored locally and fires up the synchronization to the gateway;

This function must be called in the loop function and you'll pass the number of miliseconds for verification. This should be 60.000 (1m or more, depending on your application)

```
# Receiving and processing messages from gateway
while(True):
    custom_messages = meccano.messages_process(30000)
    if len(custom_messages) > 0:
        if "MY_COMMAND" in custom_messages:
            print "Execute my command!"
        print "Custom commands received: "
        print custom_messages
    time.sleep(10)
```
