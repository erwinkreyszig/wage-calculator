# Stage 1: Build Stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies
# We use Node 20 (Current LTS) instead of 18
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    libpq-dev \
    unzip \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && curl -fsSL https://bun.sh/install | bash \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.bun/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

# 3. VERIFICATION (If this fails, the build stops here and tells us why)
RUN which unzip && unzip -v
RUN which node && node -v
RUN which bun && bun -v

# 4. Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy app code
COPY . .

# 6. Build with Debug Logging
# We use 'reflex init' first, then 'export'
RUN reflex init --loglevel debug
RUN reflex export --frontend-only --no-zip

# ---------------------------------------------------------
# Stage 2: Runtime Stage
FROM python:3.11-slim AS runner

WORKDIR /app

# 1. We need these at RUNTIME too!
# Reflex checks for unzip to manage Bun, and needs nodejs to bridge the frontend.
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    unzip \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy the installed python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 3. Copy app code and the pre-compiled frontend
COPY . .
COPY --from=builder /app/.web /app/.web

# 4. Set the path so the runner sees Node
ENV PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

ENV PYTHONUNBUFFERED=1

EXPOSE 3000 8000

# Run the app
CMD ["reflex", "run", "--env", "prod"]