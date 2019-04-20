# Simple RSS Parser

## Usage

1. Create a copy of docker-compose.yml.example to docker-compose.yml
2. Edit environment variables
3. Build and run docker containers

```bash
$ cp docker-compose.yml.example docker-compose.yml
$ docker-compose build
$ docker-compose up
```

## Running the tests

```bash
$ docker-compose run --rm app bash -c "coverage run manage.py test && coverage report -m"

```
