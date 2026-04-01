#!/bin/bash
git clone --depth 1 https://github.com/TauricResearch/TradingAgents.git temp
rm -rf temp/.git
rm -rf ./src/agent
mkdir -p ./src/agent
touch ./src/agent/.gitkeep
cp -r temp/. ./src/agent
rm -rf temp
