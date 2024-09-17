#!/bin/bash
current_dir=$(pwd)

docker run -dit \
    --name financial-concepts-cnt \
    -v $current_dir:/app \
    -p 8877-8878:8877-8878 \
    financial-concepts \
