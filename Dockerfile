FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Node.js
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI globally
RUN npm install -g @anthropic-ai/claude-code

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Claude Code SDK from GitHub
RUN pip install --no-cache-dir git+https://github.com/arthurcolle/claude-code-sdk-python.git

# Copy provider code
COPY providers/ /app/providers/
COPY claude_code_provider.py /app/claude_code_provider.py
COPY custom_handler.py /app/custom_handler.py
COPY config/ /app/config/

# Copy startup script, auth checker, and entrypoint
COPY startup.py /app/startup.py
COPY check_auth.py /app/check_auth.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 4000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:4000/health || exit 1

CMD ["/app/entrypoint.sh"]