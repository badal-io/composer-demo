FROM python:3.8.3

WORKDIR /app

EXPOSE 8000

COPY ./app/requirements.txt .

RUN pip install -r requirements.txt

COPY ./app/server.py .

CMD ["python", "/app/server.py"]