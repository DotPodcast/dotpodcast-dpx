DPX
===

Self-hosted DotPodcast environment, built in Django

[![CircleCI](https://circleci.com/gh/DotPodcast/dotpodcast-dpx.svg?style=svg)](https://circleci.com/gh/DotPodcast/dotpodcast-dpx)

DPX is a Dockerized solution for self-hosting a podcast compatible with the [DotPodcast protocol](https://dotpodcast.co/).

## Running DPX locally

You can run DPX for local development and testing by using the _docker-compose.yml_ file in this repo.

You'll also need to create a _.dockerenv_ file in the same directory, with the following:

```
PRIVATE_KEY=<set a private key for websocket service>
PUBLIC_KEY=<set a public key for websocket service>
SECRET_KEY=<set a secret key for Django>
```

Run `docker-compose up` and in a few seconds, you'll have a local development server running on _localhost:80_.

## Running tests

You can run tests using the following command:

```sh
docker-compose run web python manage.py test
```

## Running DPX in production

DPX is still under heavy development and changes will be frequent, so please take care when using DPX in production. If you use Docker Cloud and set the `dotpodcast/dpx` image to the `latest` tag, you'll always get the most up-to-date version of DPX. Later, we will setup a `stable` tag, and will encourage people to migrate to that at a later date.

You can use a similar, or adapted _docker-compose.yml_ file as above, or you can use Docker Cloud to provision your environment.

Create a stack using the following configuration:

```yaml
db:
  image: 'postgres:latest'
  volumes:
    - /var/lib/postgresql/data
redis:
  expose:
    - '6379'
  image: 'redis:latest'
web:
  autoredeploy: true
  command: /code/bin/web
  environment:
    - PRIVATE_KEY=<set a private key for websocket service>
    - PUBLIC_KEY=<set a public key for websocket service>
    - SECRET_KEY=<set a secret key for Django>
  image: 'dotpodcast/dpx:latest'
  links:
    - ws
  ports:
    - '80:8000'
  volumes_from:
    - worker
worker:
  autoredeploy: true
  command: /code/bin/worker
  environment:
    - PRIVATE_KEY=<use the websocket service private key>
    - PUBLIC_KEY=<use the websocket service public key>
    - SECRET_KEY=<use the Django secret key>
  image: 'dotpodcast/dpx:latest'
  volumes:
    - /media
ws:
  environment:
    - PRIVATE_KEY=<use the websocket service private key>
    - PUBLIC_KEY=<use the websocket service public key>
    - SECRET_KEY=<use the Django secret key>
  image: 'kjagiello/thunderpush:latest'
  ports:
    - '8080:8080'
```

This will provision a stack with a PostgreSQL node (using persistent storage), a Redis node, a websocket node (using Thunderpush), and two Django server nodes: one for undertaking background tasks, and one for serving web requests.
