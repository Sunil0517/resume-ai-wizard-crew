#!/bin/bash
# Quick start script for Resume AI Wizard

# Print colorful messages
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================${NC}"
echo -e "${BLUE}      Resume AI Wizard Starter      ${NC}"
echo -e "${BLUE}====================================${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed.${NC}"
    echo -e "${YELLOW}Please install Docker from: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed.${NC}"
    echo -e "${YELLOW}Please install Docker Compose from: https://docs.docker.com/compose/install/${NC}"
    exit 1
fi

# Check for OpenAI API key
if [ -z "${OPENAI_API_KEY}" ]; then
    echo -e "${YELLOW}Warning: OPENAI_API_KEY is not set. The application may not work correctly.${NC}"
    echo -e "${YELLOW}You can set it with: export OPENAI_API_KEY=your_key_here${NC}"
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}Building and starting the Resume AI Wizard...${NC}"
echo -e "${YELLOW}This might take a few minutes on the first run.${NC}"

# Build and start using Docker Compose
docker-compose up --build -d

echo -e "${GREEN}Application started!${NC}"
echo -e "${GREEN}You can access it at: http://localhost:8000${NC}"
echo -e "${YELLOW}To stop the application, run: ${NC}docker-compose down"
echo -e "${YELLOW}To view logs, run: ${NC}docker-compose logs -f" 