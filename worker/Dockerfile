FROM python

WORKDIR /home/worker

COPY ./*.py /home/worker/
COPY ./requirement.txt /home/worker/requirement.txt

RUN pip install -r requirement.txt

ENTRYPOINT ["/usr/local/bin/python3", "/home/worker/consumer.py"]
