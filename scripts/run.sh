#!/bin/bash
current_dir=$(pwd)

docker run -dit \
    --name market-sentiment-outlook-cnt \
    -v $current_dir:/app \
    -p 8877:8877 \
    market-sentiment-outlook \
