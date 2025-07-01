# Multi-stage build for optimal size
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local

# Install playwright browsers as root before switching user
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/playwright-browsers
ENV PYTHONPATH=/home/appuser/.local/lib/python3.11/site-packages:$PYTHONPATH
RUN python -m playwright install chromium --with-deps

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories and ensure playwright browsers are accessible
RUN mkdir -p data logs && chown -R appuser:appuser /app && \
    chmod -R 755 /opt/playwright-browsers

# Set environment variables
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

# Create startup script
RUN echo '#!/bin/bash\n\
echo "🚀 Starting GoldMiner 2.0 Enhanced services..."\n\
# Start FastAPI in background with reload for better development\n\
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload &\n\
FASTAPI_PID=$!\n\
# Wait for API to start\n\
sleep 5\n\
# Start Enhanced Streamlit UI v2\n\
python -m streamlit run app/ui/main.py --server.port 8501 --server.address 0.0.0.0 --theme.base light &\n\
STREAMLIT_PID=$!\n\
echo "✅ GoldMiner 2.0 services started!"\n\
echo "📡 API: http://localhost:8000"\n\
echo "🌐 Enhanced UI: http://localhost:8501"\n\
echo "📚 API Docs: http://localhost:8000/docs"\n\
echo "🔌 WebSocket: ws://localhost:8000/ws"\n\
echo "\n🆕 New Features:"\n\
echo "  • Real-time goldmining progress"\n\
echo "  • Edit and delete ideas"\n\
echo "  • Kanban board view"\n\
echo "  • Advanced filtering"\n\
echo "  • Export functionality"\n\
# Keep container running\n\
wait $FASTAPI_PID $STREAMLIT_PID' > /app/start.sh && chmod +x /app/start.sh

# Expose ports
EXPOSE 8000 8501

# Run both services
CMD ["/app/start.sh"]