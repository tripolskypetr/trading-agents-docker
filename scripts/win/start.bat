@echo off
for /f "usebackq eol=# tokens=1,* delims==" %%A in (".env") do set "%%A=%%B"
uv run python src/main.py
