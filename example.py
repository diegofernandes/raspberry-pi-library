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

import time
import meccano

# Connect to the server

# For connection you must provide the mac-address of your network adapter,
# The server and port where the meccano gateway is running
if not meccano.setup("66:66:66:66:66:66", "meccano.server.iot.", 80):
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
