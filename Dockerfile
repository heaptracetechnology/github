FROM          jfloff/alpine-python

ADD           app.py /app.py
ADD           server.py /server.py
RUN           pip install requests statsd flask

ENTRYPOINT   ["python", "/app.py"]
