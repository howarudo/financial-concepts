#!/bin/bash
current_dir=$(pwd)

docker run -dit \
    --name financial-concepts \
    -v $current_dir:/app \
    -p 8877:8877 \
    financial-concepts \
