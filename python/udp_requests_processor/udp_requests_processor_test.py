#!/usr/bin/env python2
""" udp_requests_processor_test

Setup the several clients and ping the udp server with almost random message
"""

import socket
import threading
from time import sleep


class ConnectionThread(threading.Thread):
    """ Connection Thread simulates client to test the server module """

    def __init__(self, id):
        """ overridden thread constructor accepts additional parameters

        Arguments:
            - id: int: client id
        """
        self.id = id
        threading.Thread.__init__(self)

    def run(self):
        """ Connects to the server and sends messages.

        Arguments:
            - None.

        Returns:
            - None.
        """

        # Connect to the server:
        client = socket.socket(socket.AF_INET,
                               socket.SOCK_DGRAM)  # UDP

        client.connect((UDP_IP, UDP_PORT))

        # Send messages with optional delay between
        for _ in xrange(100000):
            send = "id=[%i];name=[%s]" % (self.id, "Hello world")
            client.send(send)
            response = client.recv(1024)

            print send, " -> ", response

            #sleep(1)

        # Close the connection
        client.close()

UDP_IP = "127.0.0.1"    # work on localhost
UDP_PORT = 5005         # hadcoded udp port

# Let's spawn a few threads:
threads = [ConnectionThread(i) for i in xrange(200)]
for thread in threads:
    thread.daemon = True
    thread.start()

# for some time each thread will send messages
sleep(30)  # then it will end.
