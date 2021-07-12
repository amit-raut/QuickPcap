FROM alpine

# Source for tcpreplay
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories

# Fetch required dependencies
RUN apk update && apk add python3 tcpdump tcpreplay

RUN mkdir qp PCAPS
COPY QuickPcap/response.json QuickPcap/qp.py /qp/
RUN chmod +x /qp/qp.py
