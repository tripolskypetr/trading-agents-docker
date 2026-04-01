@echo off
call docker build --platform linux/amd64 -t tripolskypetr/trading-agents . -f Dockerfile
call docker push tripolskypetr/trading-agents:latest
