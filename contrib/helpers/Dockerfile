FROM python:2.7
MAINTAINER Matthias Endler <matthias.endler@trivago.com>

COPY . /benchmark
WORKDIR /benchmark
RUN pip install -r requirements.txt
RUN chmod +x run.sh

CMD ["./run.sh"]
