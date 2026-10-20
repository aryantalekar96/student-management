# =============================================================
# Dockerfile — Student Management System
# =============================================================
#
# What this file does (line by line for beginners):
#
# FROM    → Choose the base image (a pre-built OS + Python)
# WORKDIR → Set the working directory inside the container
# COPY    → Copy files from your machine INTO the container
# RUN     → Execute a command during the IMAGE BUILD step
# ENV     → Set environment variables inside the container
# EXPOSE  → Tell Docker which port the app listens on
# CMD     → The command to RUN when the container STARTS
#
# We use python:3.12-slim (not 3.14) because:
#   • 3.12 has stable wheels for all dependencies
#   • 'slim' keeps the image small (~150 MB vs ~1 GB for full)
# =============================================================

# Step 1: Start from an official Python 3.12 slim image
FROM python:3.12-slim

# Step 2: Set the working directory inside the container
#         All subsequent commands run from here
WORKDIR /app

# Step 3: Copy only requirements first (Docker cache optimization)
#         If requirements haven't changed, Docker skips re-installing
COPY requirements.txt .

# Step 4: Install Python dependencies
#         --no-cache-dir → don't cache pip downloads (saves space)
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of the application code
COPY app.py .
COPY templates/ templates/
COPY static/ static/

# Step 6: Set environment variables
#         DATABASE_PATH → where SQLite stores data inside container
#         Flask uses this in get_db()
ENV DATABASE_PATH=/app/data/students.db
ENV FLASK_ENV=production

# Step 7: Create the data directory for the SQLite database
#         In production, we'll mount a Docker volume here so data
#         survives container restarts
RUN mkdir -p /app/data

# Step 8: Tell Docker the app listens on port 5000
EXPOSE 5000

# Step 9: Create a non-root user (security best practice)
#         Running as root inside a container is a security risk
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

# Step 10: Start the Flask app using Python directly
#          host=0.0.0.0 → listen on ALL network interfaces
#          (required for Docker port mapping to work)
CMD ["python", "app.py"]
