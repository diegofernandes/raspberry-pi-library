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

import native, os, urllib2, json, time, socket, httplib

DEBUG = False

HOST = ""
PORT = 80
DEVICE_GROUP = "0"
DEVICE_ID = "Unknown"
TOKEN = ""
START_OF_OPERATION = "0"
CHECK_POINT = [0,0,0,0,0,0,0,0,0,0,0]
BLOCK_SIZE = 15

# Notifications
STATUS_NO_CONNECTION  = "0000011110";
STATUS_CONNECTION_ON  = "1111111111";
STATUS_CONNECTION_OFF = "0000000000";
STATUS_DATA_SENT      = "1010100000";
STATUS_DATA_ERROR     = "1111111110";
STATUS_BLINK          = "1010101010"

# Persistence Modes
MODE_PERSISTENT = True
MODE_NON_PERSISTENT = False


#
#   Setup the meccano library
#
def setup(ifname, host, port):
    print ""
    print "Meccano IoT"
    print "(c) 2015-2016 - Magazine Luiza"
    print "                Luizalabs"
    print ""
    time.sleep(1)
    dev = device_setup(ifname);
    if(not dev): return False
    print "Device Id: " + DEVICE_ID
    server = server_setup(host, port);
    if (not dev): return False
    reg = registration();
    if (not reg): return False
    print "Device Group   : " + DEVICE_GROUP
    print "Security Token : " + TOKEN
    clock = clock_setup();
    if (not clock): return False
    print "Start of Operation: " + START_OF_OPERATION
    checkpoint(0)
    return True

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
  global DEVICE_GROUP, TOKEN
  print "Starting Registration..."
  payload = { "device" : DEVICE_ID }
  if(DEBUG):
      print json.dumps(payload)
  headers = {
    "Content-type": "application/json",
    "Accept" : "application/json",
    "User-Agent" : "Meccano-IoT (" + native.DEVICE_NAME + ")"
  }
  if(DEBUG):
      print(headers)
  conn = httplib.HTTPConnection(HOST, PORT)
  conn.request("PUT", "/api/gateway/" + DEVICE_ID, json.dumps(payload), headers=headers)
  response = conn.getresponse()
  data = response.read()
  if(DEBUG):
      print(data)
      print response.status, response.reason
  conn.close()
  if (response.status != 200):
      print("Could not register device to network...")
      return False
  else:
      jdata = json.loads(data)
      DEVICE_GROUP = jdata["device_group"]
      TOKEN = jdata["token"]
      return True

#
#  Clock setup
#
def clock_setup():
    global START_OF_OPERATION
    print "Getting time from server..."
    # try:
    headers = { "Accept": "application/json", "Authorization": TOKEN , "User-Agent" : "Meccano-IoT (" + native.DEVICE_NAME + ")"}
    params = ""
    conn = httplib.HTTPConnection(HOST, PORT)
    conn.request("GET", "/api/gateway/" + DEVICE_ID, params, headers)
    response = conn.getresponse()
    data = response.read()
    if(DEBUG):
        print(data)
        print response.status, response.reason
    if (response.status != 200):
        print("Could not get time from server...")
        return False
    else:
        jdata = json.loads(data)
        START_OF_OPERATION = str(jdata["dateTime"])
        return True

#
#   Get the mac address
#
def get_mac_address(ifname):
    # TODO get the mac automatically
    return ifname

#
#  Set a checkpoint in time
#
def checkpoint(id):
    global CHECK_POINT
    millis = int(round(time.time() * 1000))
    CHECK_POINT[id] = millis;
    print "Checkpoint " + str(id) + " created at " + str(millis)

#
#  Check if has passed n-seconds
#
def elapsed(id, elapsed_time):
    global CHECK_POINT
    millis = int(round(time.time() * 1000))
    since_checkpoint = millis - CHECK_POINT[id]
    return(since_checkpoint >= elapsed_time)

#
#  Create the fact
#
def fact_create(channel, sensor, value):
    millis = int(round(time.time() * 1000))
    obj = {
        "channel" : channel,
        "start" : int(START_OF_OPERATION),
        "delta" : int(millis - CHECK_POINT[0]),
        "device_group" : str(DEVICE_GROUP),
        "device" : DEVICE_ID,
        "sensor" : sensor,
        "data" : value
    }
    if(DEBUG):
        print(obj)
    return json.dumps(obj)

#
#  Send fact
#
def fact_send(fact, mode):
    # Checking parameter mode
    if not ('mode' in locals()):
        mode = MODE_PERSISTENT
    print "Sending data to Meccano Network..."
    strfact = "[ " + fact + " ]"
    url = "http://" + HOST + ":" + str(PORT) + "/api/gateway/" + DEVICE_ID
    if(DEBUG):
        print url
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', TOKEN)
    req.add_header("User-Agent", "Meccano-IoT (" + native.DEVICE_NAME + ")")
    try:
        response = urllib2.urlopen(req, strfact)
    except urllib2.HTTPError as e:
        print("Could not send data to server...")
        print("Error code " + str(e.code))
        led_status(STATUS_NO_CONNECTION)
        if mode == MODE_PERSISTENT:
            data_write(fact)
        return False
    else:
        # 200
        data = response.read()
        if(DEBUG):
            print(data)
        print "Data sent successfully to the Meccano Gateway."
        print "Closing connection."
        led_status(STATUS_DATA_SENT);
        return True

#
#   Save fact to data store
#
def data_write(fact):
    # TODO implement
    f = open('data.json','a')
    f.write(fact + "\n")
    f.close()
    if(DEBUG):
        data_show()
    return True

#
#   Show the data store
#
def data_show():
    print "Fact store content: "
    with open('data.json', 'r') as f:
        for line in f:
            print line
        f.close()

#
#   Cleans the data store
#
def data_format():
    print "Formating the data store..."
    os.remove('data.json')

#
#   Check if data exists
#
def data_exists():
    return os.path.isfile("data.json")

#
#   Sync data to meccano network
#
def data_sync():
  print "Syncing data..."
  print "Check if data exists..."
  if not data_exists():
      print "There is no data to sync..."
      return False
  if(DEBUG):
	  print "==="
	  data_show();
	  print "==="
  print "Testing Connection..."
  try:
      conn = httplib.HTTPConnection(HOST, PORT)
      url = "/" + DEVICE_ID
      conn.request("GET", url)
      response = conn.getresponse()
      data = response.read()
      if response.status == 200 :
          print "Connection with the network available..."
      conn.close()
      lines = 0
      block = ""
      sync_status = True
      with open('data.json', 'r') as f:
          for line in f:
              print "Processing record " + str(lines)
              if lines >= BLOCK_SIZE:
                  block = block[:-1]
                  if(DEBUG):
                      print "Chunk:"
                      print "==="
                      print block
                      print "==="
                  # call fact_send in non persistent mode
                  # to avoid a data loop in data storage
                  if not fact_send(block, MODE_NON_PERSISTENT):
                      sync_status = False
                  block = ""
                  lines = 0
              else:
                  block += line
                  block += ","
                  lines = lines + 1
          # if there is other lines remaining, send them
          if len(block) > 0:
              block = block[:-1]
              if(DEBUG):
                  print "Chunk:"
                  print "==="
                  print block
                  print "==="
              # call fact_send in non persistent mode
              # to avoid a data loop in data storage
              if not fact_send(block, MODE_NON_PERSISTENT):
                  sync_status = False
              block = ""
              lines = 0
      if sync_status:
          # When all data sent, format local data store and start again.
          data_format()
          lines = 0
          print "Data sync finished."
      else:
          print "Could not sync data."
      f.close()
  except:
      print "No connection available to the network..."
      return False

#
#   led notification
#
def led_status(pattern):
    # TODO implement
    return True

#
#   led notification
#
def buzz_status(pattern):
    # TODO implement
    return True

#
#   Get the id of the device
#
def get_id():
    return DEVICE_ID

#
#   Get the messages/commands from server
#
def messages_execute():
    print "Getting commands from server..."
    headers = {
      "Content-type": "application/json",
      "Accept" : "application/json",
      "User-Agent" : "Meccano-IoT (" + native.DEVICE_NAME + ")",
      "Authorization" : TOKEN
    }
    if(DEBUG):
        print(headers)
    conn = httplib.HTTPConnection(HOST, PORT)
    conn.request("GET", "/api/gateway/" + DEVICE_ID, headers=headers)
    response = conn.getresponse()
    data = response.read()
    if(DEBUG):
        print data
        print response.status, response.reason
    conn.close()
    # Get commands
    jdata = json.loads(data)
    commands = jdata["messages"]
    if(DEBUG):
        print commands
    customCommands = []
    for com in commands:
        # com = com.strip("\n").strip("\r")
        if com["message"] == "REBOOT":
            print "### REBOOTING ###"
            native.reboot()
        elif com["message"] == "BLINK":
            led_status(STATUS_BLINK)
        elif com["message"] == "FORCE_SYNC":
            data_sync()
        elif com["message"] == "PURGE":
            data_format()
        else:
            customCommands.append(com)
    return customCommands


#
#   Process Messages
#
def messages_process(elapsed_time):
    # Uses the checkpoint 0 for messages processing
    if(elapsed(0, elapsed_time)):
        messages = messages_execute();
        # Check if there is data in the local device to send
        if data_exists():
            data_sync()
        # Create a new checkpoint
        checkpoint(0)
        # Return the list of custom commands/messages_process
        return messages
    else:
        return []
