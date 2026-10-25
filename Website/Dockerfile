# Deployment wrapper only. Original frontend/backend source files remain unchanged.
FROM node:20-alpine AS frontend-build
WORKDIR /build
COPY frontend-web/package*.json ./
RUN npm install
COPY frontend-web/ ./frontend-web/
COPY SKILL_VISUAL_REFERENCE_CATALOG.json ./
WORKDIR /build/frontend-web
RUN npm run build

FROM python:3.12-slim AS app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DRAFTMATE_STATIC_DIR=/app/static \
    DATABASE_PATH=/tmp/draftmate.db
WORKDIR /app/backend
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
COPY --from=frontend-build /build/frontend-web/dist /app/static
RUN mkdir -p /tmp
EXPOSE 10000
CMD ["sh", "-c", "uvicorn app.web_main:app --host 0.0.0.0 --port ${PORT:-10000}"]
