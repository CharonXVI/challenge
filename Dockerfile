FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/   
RUN pip install --no-cache-dir -r requirements.txt 

COPY . /app   
COPY DB_URL.env /app/.env

EXPOSE 5000

ENV FLASK_APP=Globant/app.py

CMD ["flask", "run", "--host=0.0.0.0"]