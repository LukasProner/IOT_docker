#FROM python:3.13-slim
#RUN pip install apprise loguru paho-mqtt pydantic pydantic-settings
#COPY src/ /app
#
#WORKDIR /app
#CMD [ "/usr/bin/env", "python", "main.py" ]

FROM python:3.13-slim
RUN groupadd --gid 1000 maker \
    && useradd --uid 1000 --gid 1000 --no-create-home maker \
    && pip3 install apprise loguru paho-mqtt pydantic pydantic-settings
COPY src/ /app
WORKDIR /app
USER maker
CMD [ "/usr/bin/env", "python3", "main.py" ]