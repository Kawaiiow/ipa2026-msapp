FROM python

WORKDIR /home/myapp

COPY ./templates/* /home/myapp/templates/
COPY ./static/* /home/myapp/static/
COPY ./app.py /home/myapp/

RUN pip install flask pymongo

EXPOSE 8080

ENTRYPOINT ["/usr/local/bin/python3", "/home/myapp/app.py"]
