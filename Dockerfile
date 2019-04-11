FROM python:3.7

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY tests_require.txt ./

RUN pip install --no-cache-dir -r requirements.txt -r tests_require.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "migrate", "&&", "python", "manage.py", "runserver", "0.0.0.0:8000"]
