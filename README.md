# Life is a Joke 😂

A simple web application that serves random jokes to brighten your day!

## Features

- 🎭 Random joke generator
- 🌐 RESTful API endpoint
- 💻 Modern, responsive web interface
- 🐳 Docker support for easy deployment
- 🏥 Health check endpoint for monitoring
- 🚀 Production-ready with Gunicorn

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (for containerized deployment)

## Quick Start

### Option 1: Run with Docker (Recommended for Server)

1. **Clone the repository**
   ```bash
   git clone https://github.com/anthony87b7f58e-coder/life_is_a_joke.git
   cd life_is_a_joke
   ```

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Open your browser and navigate to: `http://localhost:5000`
   - API endpoint: `http://localhost:5000/api/joke`
   - Health check: `http://localhost:5000/health`

4. **Stop the application**
   ```bash
   docker-compose down
   ```

### Option 2: Run Locally with Python

1. **Clone the repository**
   ```bash
   git clone https://github.com/anthony87b7f58e-coder/life_is_a_joke.git
   cd life_is_a_joke
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Copy environment file**
   ```bash
   cp .env.example .env
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your browser and navigate to: `http://localhost:5000`

## Server Deployment

### Deploy with Docker on a Server

1. **Ensure Docker and Docker Compose are installed on your server**
   ```bash
   docker --version
   docker-compose --version
   ```

2. **Clone the repository on your server**
   ```bash
   git clone https://github.com/anthony87b7f58e-coder/life_is_a_joke.git
   cd life_is_a_joke
   ```

3. **Configure environment variables (optional)**
   ```bash
   cp .env.example .env
   # Edit .env to change PORT or other settings if needed
   ```

4. **Build and start the service**
   ```bash
   docker-compose up -d --build
   ```

5. **Check service status**
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

6. **Verify health**
   ```bash
   curl http://localhost:5000/health
   ```

### Deploy with Gunicorn (Production)

For production deployments without Docker:

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run with Gunicorn**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 60 app:app
   ```

3. **Use a process manager (systemd example)**
   Create `/etc/systemd/system/life_is_a_joke.service`:
   ```ini
   [Unit]
   Description=Life is a Joke Web Application
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/life_is_a_joke
   Environment="PATH=/path/to/life_is_a_joke/venv/bin"
   ExecStart=/path/to/life_is_a_joke/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Then enable and start:
   ```bash
   sudo systemctl enable life_is_a_joke
   sudo systemctl start life_is_a_joke
   sudo systemctl status life_is_a_joke
   ```

### Nginx Reverse Proxy Configuration

For production, use Nginx as a reverse proxy:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## API Documentation

### Get Random Joke
- **Endpoint:** `GET /api/joke`
- **Response:**
  ```json
  {
    "joke": "Why don't scientists trust atoms? Because they make up everything!",
    "total_jokes": 10
  }
  ```

### Health Check
- **Endpoint:** `GET /health`
- **Response:**
  ```json
  {
    "status": "healthy",
    "service": "life_is_a_joke"
  }
  ```

### Home Page
- **Endpoint:** `GET /`
- **Response:** HTML web interface

## Configuration

The application can be configured using environment variables:

- `PORT`: Port number (default: 5000)
- `FLASK_APP`: Flask application name (default: app.py)
- `FLASK_ENV`: Environment mode (default: production)

Copy `.env.example` to `.env` and modify as needed.

## Monitoring

The application includes a health check endpoint at `/health` that can be used for:
- Docker health checks
- Load balancer health monitoring
- Uptime monitoring services
- Kubernetes liveness/readiness probes

## Technology Stack

- **Backend:** Python Flask
- **Server:** Gunicorn (WSGI HTTP Server)
- **Containerization:** Docker & Docker Compose
- **Frontend:** HTML, CSS, JavaScript (Vanilla)

## Contributing

Feel free to contribute by:
1. Forking the repository
2. Creating a feature branch
3. Making your changes
4. Submitting a pull request

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

Made with ❤️ and lots of jokes!
