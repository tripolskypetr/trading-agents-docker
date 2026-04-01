#!/bin/bash
git clone --depth 1 https://github.com/TauricResearch/TradingAgents.git temp
rm -rf temp/.git
rm -rf ./src/agent
cp -r temp ./src/agent
rm -rf temp
