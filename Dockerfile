FROM python:3

ADD bitbucket.py /

ADD config.json /

RUN pip install flask

CMD [ "python", "./bitbucket.py" ]
