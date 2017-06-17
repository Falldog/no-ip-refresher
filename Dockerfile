FROM selenium/standalone-firefox:3.4.0
LABEL authors=Falldog

RUN sudo mkdir -p /code \
    sudo chown seluser /code

COPY requirement.txt /code/requirement.txt
RUN sudo apt-get update -qqy \
    && sudo apt-get install -qqy python3-pip \
    && sudo pip3 install -r /code/requirement.txt

WORKDIR /code
COPY refresher.py refresher.py
COPY refresher.cfg refresher.cfg
COPY entry_point.sh entry_point.sh

CMD ["/code/entry_point.sh"]

