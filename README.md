# Market Sentiment Outlook

## Setup
Docker is needed for setup. [Docker](https://docs.docker.com/get-started/get-docker/) can be downloaded here. Environment inside docker is setup using poetry. This ensures that any machine with docker will be compatible.

1. Build image

```zsh
sh scripts/build.sh
```

2. Run image

```zsh
sh scripts/run.sh
```
This will create a jupyter lab server accessible on `localhost:8877`

3. Access docker container terminal

```zsh
docker exec -it market-sentiment-outlook-cnt bash
```
