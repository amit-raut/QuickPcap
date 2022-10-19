#!/bin/bash

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

banner() {
    echo ""
    echo -e "\033[36m            ╔═╗ ┬ ┬┬┌─┐┬┌─  ╔═╗┌─┐┌─┐┌─┐\033[m "
    echo -e "\033[36m            ║═╬╗│ │││  ├┴┐  ╠═╝│  ├─┤├─┘\033[m "
    echo -e "\033[36m            ╚═╝╚└─┘┴└─┘┴ ┴  ╩  └─┘┴ ┴┴  \033[m "
}

# Check to see if Docker and nc is present on the system
type docker >/dev/null 2>&1 || { echo -e >&2 "\033[31mDocker is required for QuickPcap. Please install docker first. Exiting...\033[m"; exit 1; }
type nc >/dev/null 2>&1 || { echo -e >&2 "\033[31m\`nc\` is required for QuickPcap. Please install nc first. Exiting...\033[m"; exit 1; }


# Check to see if `quickpcap` docker image is present else ask user to run install script
if [[ "$(docker images -q quickpcap 2> /dev/null)" == "" ]]; then
    echo -e "\033[0;33m\n\`quickpcap\` docker image not found locally. Please run \`install\` script first. Exiting...\033[m";
    exit 1;
fi

usage() {
    banner
    echo -e "\nUsage: ./quickpcap.sh [-h] <protocol> <port> <input-file>"
    echo "        -h         = Show this message"
    echo "        protocol   = Specify 'tcp' or 'udp' (default='tcp' if not specified, optional)"
    echo "        port       = TCP / UDP port to create PCAP for"
    echo "        input-file = a raw request file or executable like 'poc.py'"
    echo "                     executable should sends traffic to 'localhost:3333'"
    echo -e "\nExample:"
    echo "        './quickpcap.sh 80 poc.py'     (Creates PCAP after executing poc.py)"
    echo "        './quickpcap.sh udp 53 req'    (Creates PCAP by 'cat req | nc localhost:3333')"
}



# Check if only one argument is provided
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    usage
    exit 0
elif [ $# -eq 2 ]; then
    if [[ $1 -ge 1 ]] && [[ $1 -le 65535 ]]; then
        port=$1
        protocol="tcp"
    else
        echo -e "\033[0;31mERROR: Wrong port number or no input-file. Please provide TCP / UDP port from range [1-65535] and input-file\033[m"
        exit 1
    fi
elif [ $# -eq 3 ]; then
    if [ $1 == "tcp" ] || [ $1 == "TCP" ]; then
        protocol="tcp"
    elif [ $1 == "udp" ] || [ $1 == "UDP" ]; then
        protocol="udp"
    else
        echo -e "\033[31mERROR: Unsupported protocol provided. Please specify 'tcp' or 'udp' as protocol\033[m"
        exit 1
    fi
    if [[ $2 -ge 1 ]] && [[ $2 -le 65535 ]]; then
        port=$2
    else
        echo -e "\033[31mERROR: Wrong port number. Please provide TCP / UDP port from range [1-65535]\033[m"
        exit 1
    fi
else
    usage
    exit 1
fi
    

# Check to see if last argument is a file or not
for inFile; do true; done
if [[ ! -f $inFile ]]; then
    echo -e "\033[31mERROR: No input file provided. Please provide valid input file\033[m"
    exit 1
fi


dockerRun()
{
    # Create `pcap` directory in CWD and add it as volume to the QuickPcap docker container
    if [ ! -d "pcap" ]; then
        mkdir pcap;
    fi
    # Run appropriate docker command based on type of TCP / UDP port forwarding
    if [ "$protocol" == "tcp" ]; then
        docker run -d --rm --name qp -v "$(pwd)/pcap/":/PCAPS/ -p 3333:$port -ti quickpcap:latest /qp/qp.py $protocol $port > /dev/null
    else
        docker run -d --rm --name qp -v "$(pwd)/pcap/":/PCAPS/ -p 3333:$port/udp -ti quickpcap:latest /qp/qp.py $protocol $port > /dev/null
    fi
}

dockerRun
sleep 1


# Execute script if its executable else cat content of file to be dumped in PCAP
if [[ -x "$inFile" ]]; then
    ./$inFile > /dev/null
else
    if [ "$protocol" == "tcp" ]; then
        cat $inFile | nc -w 9 -c localhost 3333 > /dev/null
    elif [ "$protocol" == "udp" ]; then
        cat $inFile | nc -w 9 -u -c localhost 3333 > /dev/null
    fi
fi

sleep 3

# Check to see if PCAP is generated and inform status
pcap_name=$(echo 'QuickPcap-'$protocol'-'$port'-1')
if [[ $(ls -t pcap/ | head -n1) == "$pcap_name"* ]];  then
    find pcap/ -size  0 -delete
    mv pcap/$(ls -t pcap/ | head -n1) pcap/$(basename $inFile)-$protocol-$port-quick.pcap
    echo -e "\033[32mPCAP stored ./pcap/ directory. Thanks for using QuickPcap :)\033[m"
    if [[ -f pcap/.QuickPCAP-$protocol-$port-1.pcap ]]; then
        mv pcap/.QuickPcap-$protocol-$port-1.pcap pcap/$(basename $inFile)-$protocol-$port-quick-not-fixed.pcap
    fi
else
    echo -e "\033[31mERROR: No PCAP was generated. Please set IP:port to localhost:3333 in executable and try again. Thanks! :)\033[m"
fi

# Stop the running qp container
docker container stop qp > /dev/null &
exit 0
