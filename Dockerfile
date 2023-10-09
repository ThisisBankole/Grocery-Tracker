FROM python:3.9

COPY *.py ./

COPY /templates ./templates

COPY /tmp ./tmp

COPY swagger.yml .

COPY requirements.txt .

RUN pip install -r requirements.txt

CMD [ "python", "./app.py" ]


