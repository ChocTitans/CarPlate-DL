FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

EXPOSE 80

ENV FLASK_APP=app
ENV FLASK_ENV=production
ENV DATABASE_URL=postgresql://pfadb:serveurs..00@pfadb.postgres.database.azure.com:5432/postgres

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
