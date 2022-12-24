FROM python:3.9

WORKDIR /

COPY .   .

RUN pip install -r tequirements.txt

CMD [ "python3" ,  "main.py" ]

