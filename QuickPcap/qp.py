#!/usr/bin/env python3

#  +---------------------------------------------------------------------------+
#  |                                                                           |
#  | QuickPCAP - A quick and easy way to create and access PCAP for traffic    |
#  |             received on given TCP / UDP port                              |
#  |                                                                           |
#  | Author: Amit N. Raut                                                      |
#  |                                                                           |
#  |  This program is free software; you can redistribute it and/or modify     |
#  |  it under the terms of the GNU General Public License as published by     |
#  |  the Free Software Foundation; either version 2 of the License, or        |
#  |  (at your option) any later version.                                      |
#  |                                                                           |
#  | This program is distributed in the hope that it will be useful,           |
#  | but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#  | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             |
#  | GNU General Public License for more details.                              |
#  |                                                                           |
#  | You should have received a copy of the GNU General Public License along   |
#  | with this program; if not, write to the Free Software Foundation, Inc.,   |
#  | 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA                |
#  +---------------------------------------------------------------------------+

# List imports
import os
import time
import json
import socket
import subprocess
import datetime as dt
from threading import Thread

# Global conter for PCAP file names
counter = 0

def fake_server(port, protocol):
    """ Fake server function to send response to the traffic received on tcp / udp port
    """
    # Send standard HTTP 200 OK for traffic coming on to HTTP ports and standard response to others
    with open("/qp/response.json", "r") as f:
        response = json.loads(f.read())
    #
    http_ports = [36,80,81,82,83,84,85,86,87,88,89,90,311,383,555,591,593,631,801,808,818,901,972,1158,1220,1414,1533,1741,1830,1942,2231,2301,2381,2578,2809,2980,3029,3037,3057,3128,3443,3702,4000,4343,4848,5000,5117,5250,5450,5600,5814,6080,6173,6988,7000,7001,7005,7071,7144,7145,7510,7770,7777,7778,7779,8000,8001,8008,8014,8015,8020,8028,8040,8080,8081,8082,8085,8088,8090,8118,8123,8180,8181,8182,8222,8243,8280,8300,8333,8344,8400,8443,8500,8509,8787,8800,8888,8899,8983,9000,9002,9060,9080,9090,9091,9111,9290,9443,9447,9710,9788,9999,10000,11371,12601,13014,15489,19980,29991,33300,34412,34443,34444,40007,41080,44449,50000,50002,51423,53331,55252,55555,56712]
    #
    if os.path.isfile("/PCAPS/response") and os.path.getsize("/PCAPS/response"):
        with open("/PCAPS/response", "rb") as res_file:
            response_text = res_file.read()
    elif port in http_ports:
        response_text = response["http"].encode()
    else:
        response_text = response["non_http"].encode()
    #
    global counter
    #
    if protocol == "tcp":
        # Create socket and bind to the TCP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('',port))
            s.listen(5)
        except Exception as e:
            print("Failed to create server listening on port {0}".format(port))
        #
        # Send custom response to the clients over TCP
        try:
            while True:
                c, addr = s.accept()
                time.sleep(0.6)
                c.send(response_text)
                # c.close()
                #
                # Kill tcpdump process after serving request. I'll spawn again as its in indefinite loop
                time.sleep(1)
                pcap_number = counter
                subprocess.run(["pkill", "-f", "tcpdump"])
                #
                # Change the PCAP name and fix checksum
                pcap_name = ".QuickPcap-" + protocol + "-" + str(port) + "-" + str(pcap_number) + ".pcap"
                try:
                    with open(os.devnull) as devnull:
                        subprocess.check_call(['tcprewrite', '-C', '-i', '/PCAPS/{0}'.format(pcap_name), '-o', '/PCAPS/' + pcap_name.replace(".QuickPcap","QuickPcap").replace(".pcap","-fixed.pcap")], stderr=devnull)
                        print("Saved captured traffic in 'pcap/{0}'".format(pcap_name.replace(".QuickPcap", "QuickPcap").replace(".pcap", "-fixed.pcap")))
                except subprocess.CalledProcessError:
                    os.rename("/PCAPS/{0}".format(pcap_name), "/PCAPS/{0}".format(pcap_name.replace(".QuickPcap", "QuickPcap")) )
                    print("Saved captured traffic in 'pcap/{0}' but failed to fix checksum. Please fix checksum manually".format(pcap_name.replace(".QuickPcap", "QuickPcap")))
        except Exception as e:
            print("Something went wrong while serving request, \nERROR:{0}".format(e))

    elif protocol == "udp":
        # Create socket and bind to the UDP port
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind(('',port))
        except Exception as e:
            print("Failed to create server listening on port {0}".format(port))
        # Send custom response to the clients over TCP
        try:
            while True:
                c, addr = s.recvfrom(4096)
                time.sleep(0.6)
                s.sendto(response_text, addr)
                #
                # Kill tcpdump process after serving request. I'll spawn again as its in indefinite loop
                time.sleep(1)
                pcap_number = counter
                subprocess.run(["pkill", "-f", "tcpdump"])
                #
                # Change the PCAP name and fix checksum
                pcap_name = ".QuickPcap-" + protocol + "-" + str(port) + "-" + str(pcap_number) + ".pcap"
                try:
                    with open(os.devnull) as devnull:
                        subprocess.check_call(['tcprewrite', '-C', '-i', '/PCAPS/{0}'.format(pcap_name), '-o', '/PCAPS/' + pcap_name.replace(".QuickPcap","QuickPcap").replace(".pcap","-fixed.pcap")], stderr=devnull)
                        print("Saved captured traffic in 'pcap/{0}'".format(pcap_name.replace(".QuickPcap", "QuickPcap").replace(".pcap", "-fixed.pcap")))
                except subprocess.CalledProcessError:
                    os.rename("/PCAPS/{0}".format(pcap_name), "/PCAPS/{0}".format(pcap_name.replace(".QuickPcap", "QuickPcap")) )
                    print("Saved captured traffic in 'pcap/{0}' but failed to fix checksum. Please fix checksum manually".format(pcap_name.replace(".QuickPcap", "QuickPcap")))
        except Exception as e:
            print("Something went wrong while serving request, \nERROR:{0}".format(e))


def capture(port, protocol):
    """ Function to capture PCAP on given TCP port
    """
    #
    global counter
    counter += 1
    pcap_name = ".QuickPcap-" + protocol + "-" + str(port) + "-" + str(counter) + ".pcap"

    cmd = ['tcpdump', '-i', 'eth0', 'port', str(port), '-w', '/PCAPS/{0}'.format(pcap_name)]
    #
    with open(os.devnull) as devnull:
        capture_process = subprocess.Popen(cmd, stderr=devnull)
    try:
        while capture_process.poll() is None:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nReceived keyboard exception. Exiting...")
        capture_process.terminate()
        os._exit(1)


def is_capturing():
    """ Function to check if tcpdump process is already running
    """
    all_processes =  os.popen("ps aux").read()
    if "tcpdump" in all_processes:
        return True
    else:
        return False


def main(port, protocol):
    """ Main Function
    """
    #
    # Start server process with multiprocessing
    server_thread = Thread(target=fake_server, args=(port,protocol))
    server_thread.start()
    #
    capture(port, protocol)
    # Run capture process indefinitly and just break after each server response with flag
    while True:
        try:
            if not is_capturing():
                capture(port, protocol)
        except KeyboardInterrupt:
            print("Exiting now...\n")
            os._exit(1)


if __name__ == "__main__":
    """ QuickPcap start function
    """
    if len(os.sys.argv) < 2 or len(os.sys.argv) > 3:
        os.sys.exit(1)
    else:
        if "tcp" in os.sys.argv:
            protocol = "tcp"
        elif "udp" in os.sys.argv:
            protocol = "udp"
        else:
            protocol = "tcp"
        port = int(os.sys.argv[-1])

        print("\n==> Just send traffic to localhost:3333 with something like below\n    echo 'Test Request' | nc localhost 3333")
        print("\n==> Now you can find PCAP in '$(pwd)/pcap/' directory\n")
        main(port, protocol)
