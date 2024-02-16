FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

ENV FLASK_APP=app
ENV FLASK_ENV=production

CMD ["flask", "run"]
