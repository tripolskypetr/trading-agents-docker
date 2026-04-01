#!/bin/bash
docker build --platform linux/amd64 -t tripolskypetr/trading-agents . -f Dockerfile
docker push tripolskypetr/trading-agents:latest
