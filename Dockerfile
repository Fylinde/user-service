FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the app directory including the static directory
COPY app /app

# Make scripts executable
COPY start.sh /app/start.sh
COPY wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/start.sh /app/wait-for-it.sh

# Explicitly set PYTHONPATH
ENV PYTHONPATH=/app

CMD ["/app/start.sh"]
