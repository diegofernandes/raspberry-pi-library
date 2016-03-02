#
# Meccano IOT Gateway
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


# boolean meccano::setup(char *ssid, char *password, char *host, int port) {

import urllib2, json
import time
import socket
import httplib

DEBUG = True

HOST = ""
PORT = 80
DEVICE_GROUP = "0"
DEVICE_ID = "Unknown"
START_OF_OPERATION = "0"

def setup(ifname, host, port):
    print ""
    print "Meccano IoT"
    print "(c) 2015-2016 - Magazine Luiza"
    print "                Luizalabs"
    print ""
    time.sleep(1)
    dev = device_setup(ifname);
    print "Device Id: " + DEVICE_ID
    server = server_setup(host, port);
    reg = registration();
    print "Device Group: " + DEVICE_GROUP
    clock = clock_setup();
    print "Start of Operation: " + START_OF_OPERATION
    if DEVICE_GROUP == "0":
      print "Device Group Unknown... Setup failed"
    return (dev and server and reg and clock);

#
#   Get the device id for identification in Meccano Network
#   The python library should get the name of the computer (hostname)
#
def device_setup(ifname):
    global DEVICE_ID
    # DEVICE_ID = socket.gethostname()
    DEVICE_ID = get_mac_address(ifname)
    return True

#
# Server SETUP
#
def server_setup(host, port):
    global HOST
    global PORT
    print "Configuring server..."
    HOST = host
    PORT = port
    return True

#
#  Register device in the Meccano Gateway
#
def registration():
  global DEVICE_GROUP
  print "Starting Registration..."
  payload = { "device" : DEVICE_ID }
  if(DEBUG):
      print json.dumps(payload)
  headers = { "Content-type": "application/json" }
  conn = httplib.HTTPConnection(HOST, PORT)
  conn.request("PUT", "/api/registration/", json.dumps(payload), headers=headers)
  response = conn.getresponse()
  data = response.read()
  if(DEBUG):
      print(data)
  print response.status, response.reason
  conn.close()
  # if device doesn't exist, announce it for the gateway
  # and abort
  if data == "\"UNKNOWN_DEVICE\"":
      print "Device is not registered to Meccano Network. Announcing it."
      try:
          url = "http://" + HOST + ":" + str(PORT) + "/api/registration/"
          print url
          req = urllib2.Request(url)
          req.add_header('Content-Type', 'application/json')
          payload = { "device" : DEVICE_ID }
          if(DEBUG):
              print json.dumps(payload)
          response = urllib2.urlopen(req, json.dumps(payload))
          data = response.read()
          if(DEBUG):
              print(data)
      except:
          print "Device already announced. Waiting for approve."
      return False
  else:
    DEVICE_GROUP = data
  return True

#
#  Clock setup
#
def clock_setup():
    global START_OF_OPERATION
    print "Getting time from server..."
    conn = httplib.HTTPConnection(HOST, PORT)
    url = "/" + DEVICE_ID
    print "Binding " + url
    conn.request("GET", url)
    response = conn.getresponse()
    data = response.read()
    if(DEBUG):
        print(data)
        print response.status, response.reason
    START_OF_OPERATION = data
    conn.close()
    return True

# For testing purposes only. TODO: Implement the mac
def get_mac_address(ifname):
    return "66:66:66:66:66:66"

#
# EXAMPLE
#

setup("en0", "meccano-iot.cyclops.zone", 80)
