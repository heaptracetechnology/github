FROM          jfloff/alpine-python

ADD           app.py /app.py
RUN           pip install requests

ENTRYPOINT   ["python", "/app.py"]
