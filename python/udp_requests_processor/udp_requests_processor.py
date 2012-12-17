#!/usr/bin/env python2
"""
udp_requests_processor

@author Mykhailo "Michael" Pershyn
@date Tue Aug 7 2012

run like$: python2 ./udp_requests_processor.py 5005
then run test module (port 5005 is hardcoded in test module)

The solution is to put requests to pool and use thread pool
as this seems to be faster and more memory efficient solution.
We are saving time on threads creation / destruction as these are expensive
operations. Without thread pool we ought to create and kill
around 100 threads per second under estimated load.

###############################################################################

The assignment

You have to implement a python program that handles UDP requests.
Both input and output to the daemon should be through UDP.

The incoming request will be a string (ASCII) containing
id=[id];name=[name]
Where id is an integer, name is a string with maximum 10 characters.

The response should be a string containing
id=[id];name=[name];count=[number_of_requests]
Where number_of_requests is the total number of requests
sent to the daemon with that id.

E.g for sequential input (input)->(response)
id=1;name=foo -> id=1;name=foo;count=1
id=1;name=bar -> id=1;name=bar;count=2
id=2;name=foo -> id=2;name=foo;count=1
id=1;name=foo -> id=1;name=foo;count=3
id=2;name=bar -> id=2;name=bar;count=2

The number of requests to the daemon will be
approximately 100 requests/ second for 10 minutes
There is no requirement to produce correct results after 10 minutes
The number of unique ids will be approximately 100
The number of unique names will be approximately 100

The program should:

- listen to incoming UDP traffic on a port configurable during startup
- handle incoming requests from a main thread and have worker threads
compute the results
"""

import Queue      # importing queue module to organize pool
import socket     # for networking
import threading  # for high level work with threads
import re         # regular expressions to parse incoming message
#import argparse   # python parser command line arguments (python 2.7)
import sys


class ClientThread(threading.Thread):
    """ Thread class to process worker thread
    """

    def run(self):
        """ Run worker thread to compute the result.

            Thread will run forever, picking the work items from the pool,
            processing them, sending responses, picking another, processing ...

            Input:
            id=[id];name=[name]
            Where id is an integer, name is a string with maximum 10 characters

            The response should be a string containing:
            "id=[id];name=[name];count=[number_of_requests]"
            Where number_of_requests is the total number of
            requests sent to the daemon with that id.

            Arguments:
                - None.

            Returns:
                - None
        """
        while True:
            # get request to process
            request = requests_pool.get()

            try:
                # make sure we have actual request in variable
                if request is None:
                    continue  # skip cycle and get next request

                # Read received data
                print '%s says %s' % (request[0], request[1])

                p = re.compile("id=\[([\d]*)\];name=\[(.*)\]")
                # for 10 characters limitation
                # p2 = re.compile("id=\[([\d]*)\];name=\[([\w]{1|10}})\]")

                m = p.match(request[1])
                if m is None:
                    raise ValueError("Format of incoming message was invalid")

                r_id = int(m.group(1))
                name = m.group(2)

                # check if id is in ids_dict
                if r_id in ids_dict:  # if present - increment occurrences
                    ids_dict[r_id]["count"] += 1
                    old_name = ids_dict[r_id]["name"]
                    if old_name is None or old_name != name:
                        # Q: Name field is not clarified. Complex key???
                        # If not - What the sense then?
                        # check if equal - answer with error code
                        # and exit the method if not
                        raise ValueError("name is not expected to be \
                                          different for same ids")
                else:  # if not - add record
                    ids_dict[r_id] = {"name": name, "count": 1}

                # Form answer
                a = "id=[%i];name=[%s];count=[%i]" % (r_id,
                                                      ids_dict[r_id]["name"],
                                                      ids_dict[r_id]["count"])

                print "Answering: %s" % a

                socket.sendto(a, request[0])  # send response back to client

            except:  # if something happened - keep the server alive,
                     # notify the client
                print "Unexpected error:", sys.exc_info()[0]
                socket.sendto("Error occurred on message processing",
                              request[0])


# Parse command line arguments (python 2.7)
# parser = argparse.ArgumentParser(description="udp_requests_processor")
# parser.add_argument('port', metavar='PORT', type=int, nargs=1,
#                     help='port for the server')
# args = parser.parse_args()

# Parse command line arguments (python 2.6)
if len(sys.argv) < 2:
    print "Port not specified. Please specify port on call, e.g. 5005."
    exit()

# define connection attributes
UDP_IP = "127.0.0.1"            # work on localhost
UDP_PORT = int(sys.argv[1])     # args.port[0]  # get port from cmd line

# Create task queue
requests_pool = Queue.Queue()   # queue for incoming messages
ids_dict = {}                   # storage for ids

# Start several threads, amount of them depends on configuration
# for our case we need to process 100 requests per second,
# experimentally next amount of threads should be enough
# to work under estimated load

# Start threads
workers = [ClientThread() for _ in xrange(5)]
for worker in workers:
    worker.daemon = True  # to kill them automatically when main thread ends
    worker.start()

socket = socket.socket(socket.AF_INET,       # Internet
                       socket.SOCK_DGRAM)    # UDP
socket.bind((UDP_IP, UDP_PORT))              # bind to socket

print "Server initialized at %s:%i" % (UDP_IP, UDP_PORT)

while True:  # run server thread until interrupted by special signal
    data, addr = socket.recvfrom(1024)

    if data == "Dear server please die":
        # TODO: remove this if remove shutdown should be avoided
        print "Die message received. Killing threads..."
        # threads are daemons, will be killed automatically on program end
        break

    # put request data to pool to be processed by threads
    requests_pool.put((addr, data))

socket.close()  # this code is called in GC anyway...
