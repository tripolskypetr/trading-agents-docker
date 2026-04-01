#!/bin/bash
git clone https://github.com/TauricResearch/TradingAgents.git temp
rm -rf ./src/agent
cp -r temp ./src/agent
rm -rf temp
