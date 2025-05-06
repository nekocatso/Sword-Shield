FROM python:3.13.2-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set up the working directory
WORKDIR /opt/Sword_Shield

# Install system dependencies required for Pyppeteer and other operations
# Combined into a single RUN statement to reduce layers
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # Dependencies for Pyppeteer (headless Chrome)
    libnss3 libxss1 libasound2 libatk1.0-0 libcairo2 libcups2 libdbus-1-3 \
    libexpat1 libfontconfig1 libgbm1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 \
    libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libx11-6 libx11-xcb1 \
    libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 \
    libxrandr2 libxrender1 libxtst6 ca-certificates fonts-liberation lsb-release \
    xdg-utils wget vim libgomp1 \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements.txt to leverage Docker cache
COPY ./requirements.txt /opt/Sword_Shield/requirements.txt

# Install Python dependencies
# Using a trusted host for pip mirror
RUN python -m pip install --upgrade pip -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com && \
    python -m pip install --no-cache-dir -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

# Copy the rest of the application code
COPY ./ /opt/Sword_Shield/

# Create a non-root user and group
RUN groupadd -r appgroup && useradd -r -g appgroup -ms /bin/bash appuser

# Copy entrypoint script and make it executable
COPY ./entrypoint.sh /opt/Sword_Shield/entrypoint.sh
RUN chmod +x /opt/Sword_Shield/entrypoint.sh

# Switch to non-root user
USER appuser

# Expose the port Gradio runs on
EXPOSE 7860

# Command to run the application using the entrypoint script
CMD ["/opt/Sword_Shield/entrypoint.sh"]