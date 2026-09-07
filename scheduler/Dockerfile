FROM python

WORKDIR /home/scheduler

COPY ./*.py /home/scheduler/
COPY ./requirement.txt /home/scheduler/requirement.txt

RUN pip install -r requirement.txt

CMD ["/usr/local/bin/python3", "/home/scheduler/scheduler.py"]
