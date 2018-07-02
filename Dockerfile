FROM python:3

ADD bitbucket.py /

ADD config.json /

RUN pip install flask
RUN pip install requests
#RUN pip install https://github.com/dianakhuang/pytumblr/archive/diana/python-3-support.zip

CMD [ "python", "./bitbucket.py" ]
