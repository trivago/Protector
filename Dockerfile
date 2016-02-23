FROM python:2.7
MAINTAINER Matthias Endler <matthias.endler@trivago.com>

COPY . /protector
WORKDIR /protector
RUN python setup.py install
EXPOSE 8888
RUN chmod +x run.sh

CMD ["./run.sh"]
