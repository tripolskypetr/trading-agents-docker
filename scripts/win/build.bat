@echo off
call git clone --depth 1 https://github.com/TauricResearch/TradingAgents.git temp
rd /s /q temp\.git
rd /s /q src\agent
xcopy /e /i /h /q temp src\agent
rd /s /q temp
