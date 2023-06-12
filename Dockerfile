FROM python:3.9

RUN apt update

#download and install chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

COPY . .
WORKDIR .
RUN pip install -r requirements.txt
RUN apt install -y chromium-driver
CMD tail -f /dev/null
CMD [ "python", "main.py", "pytest tests/"]
