FROM python:3.9

WORKDIR /

COPY .   .

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

CMD [ "python3" ,  "main.py" ]

