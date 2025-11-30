@echo off
cd /d %~dp0
uv run --group dev pytest tests/integration/ -v
