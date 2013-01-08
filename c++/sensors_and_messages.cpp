// @author: Michael Pershyn

// please compile this code with
//> clang++ -std=c++11 -pthread ./sensors_and_messages.cpp
//> g++ -std=c++11 -pthread ./sensors_and_messages.cpp

/* There is a network of N (initial parameter) sensors given.
// Each sensor is connected to M other sensors (initial parameter) - randomly selected.
// Sensors can exchange messages between themselves.

// Initially,
// each sensor has a one message with one specific recipient, which message
// has to be sent to a randomly chosen neighbor/recipient (of connected sensor)
// if he is not the addressee of precisely this message. The task is to write
// a simulation in which each sensor will operate in its own thread
//  (a necessary condition). The completion of the task is to stop the
// transmission. The simulator has to be designed in the way – that for each
//  message counts the number of times it has been communicated/transmitted
// (hop count) and writes to the standard output below histogram:

// N-hops      M-times
// R-hops      S-times

// At the same time it has to be sorted in ascending order by the number of hops.
// The application should work seamlessly with large numbers of threads (MUST condition!).
// This means no "busy waiting"
*/

#include <map>
#include <list>
#include <thread>
#include <mutex>

#include <iostream>

// each sensor will operate in its own thread
// seamless with large number of threads


/* Message has hops and destination edge id
*/
struct Message
{
    int dest_id;
    int hops;
};


/* Sensor
*
* has:
* - sensor id,
* - list of incoming message
* - thread body
* - list of connected nodes
*/
class Sensor
{
    int node_id;

    // connection id's (size - M)
    int connections[];

    // incoming messages list
    std::list<Message*> messageList;

    // mutex to lock to write to message list and read from it.
    std::mutex messageListMutex;

    public:

    void processMessages()
    {
        messageListMutex.lock();

        Message* pmsg = messageList.front();
        messageList.pop_front();

        if (node_id == pmsg->dest_id)
        {
            // message reached it's destination
            // add message to results container
            // ...

        }else
        {
            // if not - send it randomly to one of the connections
            // ...
        }

        messageListMutex.unlock();

        // once message is processed - check if the results container is full.
        // if yes - then join the thread.

        // ....
    }
};


// store shared dict of sensors: id->sensor ptr
// ... sensors... read only during the simulation.
std::map<int, Sensor*> sensors;


/** Initializes N sensors with M random connections each.
 * Then initializes initial messages and starts the simulation
 *
 * @param N - Amount of sensors
 * @param M - Amount of connection for each param
 *
 */
void initialize_sensors(int N, int M)
{

// Assume additional condition to exclude probability of cycled simulation
// what is the smallest M that will guarantee that graph is connected.
// (2*m + 2) > N

// ...

}


void test_thread()
{
    std::cout << "hello from thread..." << std::endl;
}


int main( int argc, char *argv[] )
{
    std::cout << "calling the thread" << std::endl;

    // launch a thread
    std::thread t( test_thread );

    // join a thread with main thread
    t.join();

    return 0;
}
