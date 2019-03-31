FROM python:3.7

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

RUN set -ex && apt-get update \
    && apt-get install -y --no-install-recommends mysql-client \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY requirements.txt ./
COPY tests_require.txt ./

RUN pip install --no-cache-dir -r requirements.txt -r tests_require.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "migrate", "&&", "python", "manage.py", "runserver", "0.0.0.0:8000"]
