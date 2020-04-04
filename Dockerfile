FROM python:3.7-alpine
LABEL mainteiner 'Artur Henrique <artur_henriquebs@hotmail.com>'

RUN apk add mosquitto && \
    apk add mosquitto-clients && \ 	
    pip install paho-mqtt && \
    mkdir /app && \
    touch app/code.js

WORKDIR /app 	
# with -u it is possible to see output with docker log command
CMD [ "python","-u" , "./code.py"  ]



# docker run --name mqtt -v $(pwd)/app/sub.py:/app/code.py mqtt