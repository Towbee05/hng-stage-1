FROM python:3.14

RUN mkdir /app

WORKDIR /app

ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
