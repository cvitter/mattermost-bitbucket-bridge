FROM python:3

ADD bitbucket.py /
ADD helpers.py /
ADD config.json /

RUN pip install flask
RUN pip install requests

CMD [ "python", "./bitbucket.py" ]
