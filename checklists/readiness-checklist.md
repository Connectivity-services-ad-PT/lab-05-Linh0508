# Readiness Checklist – Lab 05

## Status Summary ✅

- [x] **Database ready** – PostgreSQL running, healthy ✅
- [x] **AI service ready** – Returning 200 on /health ✅  
- [x] **API ready** – Returning 200 on /health ✅
- [x] **Environment variables** – .env configured correctly ✅
- [x] **Network & Ports** – All services mapped and communicating ✅
- [ ] **Image tags** – TODO: tag and push to registry

## Detailed Check Results

### 1. Database (PostgreSQL)
```bash
$ docker compose exec db pg_isready -U lab05
/var/run/postgresql:5432 - accepting connections
```
✅ Status: HEALTHY (since 08:29 UTC)

### 2. AI Service  
```bash
$ curl http://localhost:9000/health
{"status":"ok","service":"ai-service","version":"0.5.0"}
```
✅ Status: HEALTHY - Returns 200 OK

### 3. API Service
```bash
$ curl http://localhost:8000/health
{"status":"ok","service":"iot-ingestion","version":"0.5.0"}
```
✅ Status: HEALTHY - Returns 200 OK

### 4. Environment & Configuration
- APP_PORT=8000 ✅
- POSTGRES_USER=lab05 ✅
- POSTGRES_PASSWORD=lab05pass ✅
- AUTH_TOKEN=local-dev-token ✅
- SERVICE_VERSION=0.5.0 ✅

### 5. Docker Network & Port Mapping
- Network `team-internal` created ✅
- API port 8000 → 8000 ✅
- AI port 9000 → 9000 ✅
- DB port 5432 → 5432 ✅

## Session Log

**2026-06-11 08:19-08:30 UTC** - Debug & Fix Session

### Issues Found & Fixed
1. **AI Service: ModuleNotFoundError for fastapi**
   - Cause: image python:3.11-slim has no fastapi installed
   - Fix: Created Dockerfile.ai with pip install fastapi uvicorn pydantic requests
   - Updated docker-compose.yml to build from Dockerfile.ai

2. **Database: "database 'lab05' does not exist"**
   - Cause: Database not auto-created on startup
   - Fix: PostgreSQL POSTGRES_DB env var auto-creates it, just need to wait for startup

3. **docker-compose.yml: version field obsolete**
   - Fix: Removed `version: "3.8"` from file

### Action Taken
```bash
docker compose down -v              # Remove old containers
docker compose up -d --build        # Rebuild and start
docker compose ps                   # Verify all healthy
```

## Test Evidence
- [x] All 3 services running and healthy
- [x] All health endpoints returning 200 OK
- [x] Environment configured correctly
- [ ] TODO: Run Postman/Newman tests
- [ ] TODO: Create reports/screenshots
- [ ] TODO: Tag images v0.1.0-<team> and push to registry

## Next Steps
1. Test API POST /readings endpoint with auth token
2. Verify AI service /predict endpoint 
3. Run Newman test suite
4. Tag and push images
5. Add test reports to reports/ directory
