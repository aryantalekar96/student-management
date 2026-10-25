# =============================================================================
# Dockerfile — Student Management System
# =============================================================================
#
# A Dockerfile is a recipe for building a Docker image.
# Docker reads it top to bottom and creates a layered image.
#
# Build command:  docker build -t student-management:v1 .
# Run command:    docker run -p 5000:5000 student-management:v1
# =============================================================================

# INSTRUCTION 1: FROM
# -------------------
# Start from an official Python 3.11 image (slim = smaller size, no extras).
# Think of this as inheriting a kitchen that already has Python installed.
# We don't need to install Python ourselves — it's already in this base image.
FROM python:3.11-slim

# INSTRUCTION 2: WORKDIR
# ----------------------
# Set the working directory INSIDE the container to /app.
# All commands from here on will run in /app.
# This is like "cd /app" but it also creates the folder if it doesn't exist.
WORKDIR /app

# INSTRUCTION 3: COPY requirements.txt first (Docker caching trick)
# -----------------------------------------------------------------
# We copy requirements.txt BEFORE the rest of the code.
# Why? Docker caches each layer. If requirements.txt hasn't changed,
# Docker skips the pip install step (faster builds).
COPY requirements.txt .

# INSTRUCTION 4: RUN pip install
# --------------------------------
# Install all Python libraries listed in requirements.txt.
# --no-cache-dir = don't save pip's download cache (keeps image smaller).
RUN pip install --no-cache-dir -r requirements.txt

# INSTRUCTION 5: COPY the rest of the app
# ----------------------------------------
# Copy everything from your project folder (.) into /app inside the container.
# The .dockerignore file (if present) controls what gets excluded.
COPY . .

# INSTRUCTION 6: EXPOSE
# ----------------------
# Tell Docker "this container will listen on port 5000."
# This is documentation — it doesn't actually open the port.
# The -p flag in docker run is what actually maps the port.
EXPOSE 5000

# INSTRUCTION 7: ENV (Environment Variables)
# -------------------------------------------
# Set environment variables inside the container.
# FLASK_ENV=production → disables debug mode (important for real deployments).
# PYTHONUNBUFFERED=1   → makes Python print output immediately (shows in logs).
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# INSTRUCTION 8: CMD
# ------------------
# The command to run when the container STARTS.
# We use python app.py to start the Flask server.
# CMD = default command. Can be overridden at runtime.
CMD ["python", "app.py"]
