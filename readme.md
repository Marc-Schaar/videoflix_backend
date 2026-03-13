# ![Videoflix Logo](static/images/logo_.png)  Backend API

This is a high-performance video streaming REST API, inspired by Netflix, built with **Django** and **Django REST Framework**.
The platform features automated video processing via **ffmpeg**, background task queuing with **Redis**, and a fully containerized environment using **Docker**.

## Features
- User Authentication: Secure registration, login, and password reset functionality.
- Video Streaming: Optimized video delivery for a seamless viewing experience.
- Automated Video Processing: Integration with ffmpeg to convert uploaded videos into multiple resolutions (e.g., 480p, 720p, 1080p).
- Background Tasks: Handling of heavy video processing tasks to ensure API responsiveness (using Redis/RQ).
- Containerization: Fully Dockerized setup for Database, Cache, and Application..
- Database: Reliable data management with PostgreSQL.
- Automated Setup: Superuser creation and database initialization handled via environment variables.


## Requirements & Installation Dependencies

To run this project, you need the following tools installed on your system.

### 1. Docker & Docker Compose (Recommended)
The easiest way to run the project. Docker handles Python, PostgreSQL, Redis, and ffmpeg automatically.
* **Windows/macOS:** Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
* **Linux:** [Install Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/).

### 2. Manual Installation (Alternative)
If you want to run the project without Docker, install these dependencies:

#### **Python 3.10+**
Download from [python.org](https://www.python.org/downloads/) or use your package manager:

#### **FFMPEG**
Required for video transcoding and resolution processing.

```bash
# Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg

# Arch Linux
```bash
sudo pacman -S ffmpeg

# macOS (Homebrew)
brew install ffmpeg

# Windows (Chocolatey)
choco install ffmpeg
```

#### Redis
Required for the background worker (RQ).
```bash
# Ubuntu/Debian
sudo apt install redis-server

# macOS (Homebrew)
brew install redis

# Windows
# Use Memurai or run Redis via WSL2 (recommended)
```

## Setup & Installation

### 1. Clone the repository:

```bash
git clone https://github.com/Marc-Schaar/videoflix_backend.git
cd videoflix_backend
```

### 2. Create and activate a virtual environment:

```bash
python3 -m venv env

# macOS/Linux
source env/bin/activate  

# Windows
.\env\Scripts\activate 
```

### 3. Install dependencies:

```bash
pip install -r requirements.txt
```

### 4. Apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a `.env` file:

The project requires a `.env` file in the root directory. You can create one by copying the provided template:

**macOS / Linux / Git Bash:**
```bash
cp env.sample .env
```

**Windows (Command Prompt):**
```bash
copy env.sample .env
```

**Windows (PowerShell):**
```bash
cp env.sample .env
```


### 4. Deployment with Docker (Recommended)
The easiest way to get the project running is using Docker Compose. This starts the Django app, the PostgreSQL database, and the Redis worker.

```bash
docker-compose up --build
```

### (Optional) Run the development server:

```bash
python manage.py runserver
```


## Usage
API base URL: http://127.0.0.1:8000/api/

## Authentication
Token-based authentication is used.
Obtain a token via the login endpoint and include it in the request header:

```bash
Authorization: Token <your_token>
```

## Architecture & Workflow
- API (Django): Handles requests and manages the database.
- Worker (Redis/ffmpeg): When a video is uploaded, a background task is sent to the worker.
- Transcoding: The worker uses ffmpeg inside the container to generate multiple stream qualities.
- Storage: Media files are stored in persistent Docker volumes.

## About the Project
Videoflix is the final "Capstone" project of the Developer Academy Backend course. It demonstrates the ability to architect a complex system involving media processing, asynchronous task execution, and modern DevOps practices like containerization.





