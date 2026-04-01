# Clone TradingAgents source into ./src/agent
build:
	bash scripts/linux/build.sh

# Build and push Docker image to Docker Hub
publish:
	bash scripts/linux/publish.sh

# Load .env and run src/main.py locally via uv
start:
	bash scripts/linux/start.sh
