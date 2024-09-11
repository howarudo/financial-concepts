#!/bin/bash
current_dir=$(pwd)

docker run -dit \
    --name market-trade-analysis \
    -v $current_dir:/app \
    -p 8877:8877 \
    market-trade-analysis \
