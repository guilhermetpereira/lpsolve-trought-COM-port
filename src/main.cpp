/**
 * @file /example1/main.cpp
 * @author Philippe Lucidarme
 * @date December 2019
 * @brief File containing example of serial port communication
 *
 * This example send the ASCII table through the serial device
 *
 * @see https://lucidar.me
 */


// Serial library
#include "../inc/serialib.h"
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <signal.h>
#include <vector>
#include <iostream>
#include <algorithm>
#include <string.h>
#include <math.h>

#define TIME_COUNTER 1
#define PRINT 0

#if TIME_COUNTER
#include <chrono>
#endif



#if defined (_WIN32) || defined(_WIN64)
    #define SERIAL_PORT "COM9"
#endif
#ifdef __linux__
    #define SERIAL_PORT "/dev/ttyACM0"
#endif


using namespace std;




typedef enum {
    STATE_WAIT_COMMAND,
    STATE_RX_STORE,
    STATE_SOLVE_COOP,
    STATE_IDLE
}AppState_t;

typedef struct nodes_info_t
{
    uint8_t assigned_time_slot;
    int energy;       
    uint8_t neighbors[50]; // size limited by hardware
}nodes_info_t;
serialib serial;
vector<uint8_t> buffer;
vector<nodes_info_t> nodes_info_vec;
uint8_t assTimeSlot;
/*
    Message specifation:
    1. # Associated Nodes (uint8_t)
    2. new node info signal 'N'
    3. node_info_t
    4. finsh node info signal 'F'
    5. back to 2 or end of buffer
*/
void process_data(void)
{
    nodes_info_vec.clear();
    assTimeSlot = (uint8_t)buffer.front() - 48;
    buffer.erase(buffer.begin());
    nodes_info_t tmp_data;
    for (;buffer.size() > 0;)
    {
        std::vector<uint8_t>::iterator it = buffer.begin();
        if (*it == 'N')
        {
            buffer.erase(buffer.begin());
            std::vector<uint8_t>::iterator v = find(buffer.begin(),buffer.end(), 'N');
            tmp_data.assigned_time_slot = buffer.front();
            tmp_data.energy =   (uint32_t)(((int)buffer.at(1) - 48) << 4)  | (uint32_t)(((int)buffer.at(2) - 48) << 0) |
                                (uint32_t)(((int)buffer.at(3) - 48) << 12) | (uint32_t)(((int)buffer.at(4) - 48) << 8) |
                                (uint32_t)(((int)buffer.at(5) - 48) << 20) | (uint32_t)(((int)buffer.at(6) - 48) << 16)|
                                (uint32_t)(((int)buffer.at(7) - 48) << 28) | (uint32_t)(((int)buffer.at(8) - 48) << 24);
            memset(tmp_data.neighbors, 0, sizeof(tmp_data.neighbors));
            int j = 0;
            for (uint8_t i = 0; i < (int)ceil(assTimeSlot/8.0); i++)
            {
                tmp_data.neighbors[j++] =   ((int)buffer.at(9+i) > 96) ? (uint32_t)(((int)buffer.at(9+i) - 87) << 0) : (uint32_t)(((int)buffer.at(9+i) - 48) << 0) |
                                            ((int)buffer.at(10+i) > 96 ) ? (uint32_t)(((int)buffer.at(10+i) - 87) << 4) : (uint32_t)(((int)buffer.at(10+i) - 48) << 4);
            }
            nodes_info_vec.push_back(tmp_data);
            buffer.erase(buffer.begin(), v);
        }
    }

}

int main( /*int argc, char *argv[]*/)
{

    AppState_t state = STATE_WAIT_COMMAND;
    char signal = 0;

    #if TIME_COUNTER
    chrono::steady_clock sc;
    chrono::steady_clock::time_point begin, end;
    #endif

    // Connection to serial port
    char errorOpening = serial.openDevice(SERIAL_PORT, 115200);
    
    // If connection fails, return the error code otherwise, display a success message
    if (errorOpening!=1) return errorOpening;
    printf ("Successful connection to %s\n",SERIAL_PORT);
    
    serial.flushReceiver();
    system("cls");
    for (;;)
    {
        switch(state)
        {
            case STATE_WAIT_COMMAND:
            if(serial.readChar(&signal)==1)
            {
                /* Check if Received signal is node info */
                #if PRINT
                cout << "\nReceived Signal : " << signal << endl;
                #endif
                if(signal == 'S')
                {
                    #if TIME_COUNTER
                    begin = std::chrono::steady_clock::now();
                    #endif
                    state = STATE_RX_STORE;
                }
                else
                    state = (buffer.size() >= 0) ? STATE_SOLVE_COOP : STATE_WAIT_COMMAND;
            }
            else
            {
                #if PRINT
                cout << "No Signal received" << endl;
                #endif
                // todo : enviar sinal de erro pro pan ??
                state = STATE_IDLE;
            }
            break;
            case STATE_RX_STORE:

                /* Read COM until end of transmission */
                int err;
                for (;((err = serial.readChar(&signal)) == 1) && signal != 'T';)
                {
                    buffer.push_back(signal);
                }
                buffer.push_back(signal);

                #if PRINT
                for (vector<uint8_t>::const_iterator i = buffer.begin(); i != buffer.end(); ++i)
                         std::cout << *i << ' ';
                cout << endl;
                #endif

                /* check if there is new transmission on COM buffer */
                state = ( serial.available() > 0 ) ? STATE_WAIT_COMMAND : STATE_SOLVE_COOP;
            break;
            case STATE_SOLVE_COOP:

            #if PRINT
            cout << "Solve COOP" << endl;
            #endif
            #if TIME_COUNTER
            end = std::chrono::steady_clock::now();
            cout << "Elapsed time (before process) = " << chrono::duration_cast<chrono::milliseconds>(end - begin).count() << " [miliseconds]" << endl;
            #endif
            process_data();
            /* Processe data */
            // cout << (int)assTimeSlot << endl;
            // for (vector<nodes_info_t>::const_iterator i = nodes_info_vec.begin(); i != nodes_info_vec.end(); ++i)
            // {
            //     cout << "\nNode's tTS = " << i->assigned_time_slot << "\nenergy = " << i->energy << "\nBitmap: " <<endl;
            //     for (int j = 0; j < assTimeSlot; ++j)
            //     {
            //        cout << (int)i->neighbors[j] << " " ;
            //     }
            // }

            #if TIME_COUNTER
            end = std::chrono::steady_clock::now();
            cout << "Elapsed time (after process)  = " << chrono::duration_cast<chrono::milliseconds>(end - begin).count() << " [miliseconds]" << endl;
            #endif

            Sleep(1000);
            state = STATE_WAIT_COMMAND;
            break;
            case STATE_IDLE:
            break;
        }
    }

    // Close the serial device
    serial.closeDevice();

    return 0 ;
}
