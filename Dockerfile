FROM ubuntu:22.04

COPY requirements.txt /requirements.txt

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends\
    python3 python3-pip && \
    pip3 install --upgrade pip && \
    pip3 install -r requirements.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /action

COPY review.py /action/review.py
COPY review /action/review

ENTRYPOINT ["/action/review.py"]
