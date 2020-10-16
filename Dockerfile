FROM python:3.8

WORKDIR /usr/src/app

#COPY requirements.txt /requirements.txt
COPY ./ /usr/src/app

RUN pip install -r  /usr/src/app/requirements.txt

EXPOSE 5000

CMD ["python", "/usr/src/app/app.py"]