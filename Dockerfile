FROM python:3.7-slim 

COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app

RUN mkdir /app/logs

EXPOSE 8000

CMD ["python3", "bot.py"]