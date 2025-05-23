FROM python:3.10-slim as backend

WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy language model
RUN python -m spacy download en_core_web_lg

# Copy Python backend files
COPY app.py .
COPY setup.py .
COPY agents/ agents/
COPY templates/ templates/

# Stage 2: Frontend build
FROM node:18-slim as frontend

WORKDIR /app

# Copy frontend files
COPY package*.json ./
COPY tsconfig*.json ./
COPY vite.config.ts ./
COPY index.html ./
COPY postcss.config.js ./
COPY tailwind.config.ts ./
COPY components.json ./
COPY public/ public/
COPY src/ src/

# Install dependencies and build frontend
RUN npm install
RUN npm run build

# Stage 3: Final image
FROM python:3.10-slim

WORKDIR /app

# Copy backend files from backend stage
COPY --from=backend /app .
COPY --from=backend /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=backend /usr/local/bin/ /usr/local/bin/

# Copy frontend build files
COPY --from=frontend /app/dist/ ./dist/

# Create symlink for FastAPI to serve frontend
RUN ln -s dist frontend

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["python", "app.py"] 