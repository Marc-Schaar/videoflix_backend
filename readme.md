# ![Videoflix Logo](static/images/logo.svg)  Backend API

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

### 2. Manual Installation (Development Only)
If you wish to run the project outside of Docker, you must install:
- **Python 3.12+**
- **FFMPEG:** 
- **Redis:** 

#### **Python 3.10+**
Download from [python.org](https://www.python.org/downloads/) or use your package manager:

#### **FFMPEG**
Required for video transcoding and resolution processing.

```bash
# Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg

# Arch Linux
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

### 2. Create a `.env` file:

The project uses a .env file for all sensitive settings and automated setup. You can create one by copying the provided template:

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


### 3. Deployment with Docker (Recommended)
The easiest way to get the project running is using Docker Compose. This starts the Django app, the PostgreSQL database, and the Redis worker.

```bash
docker-compose up --build
```

**During the first start, the system will**:
1. Wait for PostgreSQL to be ready.
2. Apply all database migrations.
3. Automatically create a Superuser using the credentials from your .env file.
4. Start the Gunicorn server and the RQ-Worker.
 
### Manual Setup (Alternative)
If you prefer to run it locally without Docker:

1. **Setup Virtual Environment**:
```bash
python3 -m venv env
source env/bin/activate  # Windows: .\env\Scripts\activate
pip install -r requirements.txt
```
2. **Run Migrations & Server**:
```bash
python manage.py migrate
python manage.py runserver
```
3. **Start the Worker (separate terminal)**:
```bash
python manage.py rqworker default
```


## Usage

### Video Management (Admin Panel)
Content management is handled via the Django Admin interface.
1. Log in to the Admin Panel: http://127.0.0.1:8000/admin/
2. Use the Superuser credentials defined in your .env.
3. Upload Videos: Navigate to the Videos section to upload new files.

**Note**: Upon saving, the background worker will automatically trigger ffmpeg to process the video into multiple resolutions.

### API Access
**API Base URL**: http://127.0.0.1:8000/api/
**API Admin Panel**: http://127.0.0.1:8000/admin/

## Authentication
Token-based authentication is used.
Obtain a token via the login endpoint and include it in the request header:

```bash
Authorization: Token <your_token>
```

## Architecture & Workflow
- **API (Django)**: Powered by Gunicorn, handles REST requests and metadata.
. **Content Upload**: Videos are uploaded via the Admin Panel and stored in the media/ volume.
- **Worker (Redis/ffmpeg)**: When a video is uploaded, a background task is sent to the worker.
- **Transcoding**: The worker uses ffmpeg inside the container to generate multiple stream qualities.

## About the Project
Videoflix is the final "Capstone" project of the Developer Academy Backend course. It demonstrates the ability to architect a complex system involving media processing, asynchronous task execution, and modern DevOps practices like containerization.





