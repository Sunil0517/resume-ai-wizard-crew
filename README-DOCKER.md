# Running Resume AI Wizard with Docker

This application can be run using Docker, which eliminates environment and dependency issues.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)

## Setting Up

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/resume-ai-wizard-crew.git
   cd resume-ai-wizard-crew
   ```

2. If you plan to use OpenAI's API, set your API key:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

## Running the Application

1. Build and start the application using Docker Compose:
   ```bash
   docker-compose up
   ```

   This will:
   - Build the Docker image
   - Install all dependencies
   - Build the frontend
   - Start the FastAPI server

2. Access the application at:
   ```
   http://localhost:8000
   ```

3. To stop the application:
   ```bash
   docker-compose down
   ```

## Development

- The Docker setup mounts the `./agents` directory as a volume, allowing you to modify the Python agent code without rebuilding the container.
- If you need to make other backend changes, you should rebuild the container:
  ```bash
  docker-compose up --build
  ```

## Troubleshooting

1. If you encounter issues with the Docker build:
   - Check the Docker logs: `docker-compose logs`
   - Try rebuilding without cache: `docker-compose build --no-cache`

2. If you have issues with OpenAI API:
   - Ensure your API key is properly set
   - Check if the API key has the necessary permissions and credits

3. If the FastAPI server fails to start:
   - Check the logs for Python exceptions
   - Ensure port 8000 is not already in use on your system 