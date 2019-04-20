# Simple RSS Parser

[![CircleCI](https://circleci.com/gh/daniyarchambylov/rss-parser.svg?style=svg)](https://circleci.com/gh/daniyarchambylov/rss-parser)
[![Coverage Status](https://coveralls.io/repos/github/daniyarchambylov/rss-parser/badge.svg?branch=master)](https://coveralls.io/github/daniyarchambylov/rss-parser?branch=master)

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
