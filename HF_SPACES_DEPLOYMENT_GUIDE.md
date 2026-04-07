# HF Spaces Deployment Guide for LUNAR

This guide ensures smooth, stable deployment of LUNAR on HuggingFace Spaces.

## Prerequisites

- HuggingFace account with Spaces access
- GitHub repository linked to HF Spaces (automatic sync)
- Docker support enabled (default on HF Spaces)

## Deployment Configuration

### HF Spaces Settings

1. **Space Name**: `lunar`
2. **SDK**: Docker  
3. **Space Type**: Public (for leaderboard access)
4. **Region**: Recommended closest to your location

### Environment Variables (Set in HF Spaces Settings)

```
PORT=7860              # HF Spaces default port (REQUIRED)
HOST=0.0.0.0           # Listen on all interfaces
WORKERS=1              # Single worker for stability
RELOAD=false           # Production mode (no file watching)
SESSION_TIMEOUT=2      # Auto-cleanup old sessions (hours)
MAX_SESSIONS=100       # Memory management cap
```

## Optimization for Stability

### 1. Session Management
- **Auto-Cleanup**: Old sessions cleaned up automatically every 2 hours
- **Max Sessions**: Limited to 100 concurrent sessions
- **Memory Bounds**: Prevents unbounded memory growth

### 2. Health Monitoring  
- **Health Checkpoint**: Every 30 seconds
- **Startup Wait**: 30 seconds before declaring ready
- **Timeout**: 15 seconds per health check with 5 retries

### 3. Performance Tuning
- **Timeouts**: 60-second timeout for long-running tasks
- **Keep-Alive**: 30-second timeout prevents hanging connections
- **Workers**: Single worker ensures predictable resource usage

### 4. Dockerfile Optimizations
```dockerfile
# Minimal dependencies - only curl for health checks
# No build-essential (not needed for runtime)
# Slim Python image reduces startup time
# Production health checks with longer timeouts
```

## Monitoring the Deployment

### Check Status
- **Live URL**: `https://mehajabeen-lunar.hf.space`
- **Health Endpoint**: `https://mehajabeen-lunar.hf.space/health`
- **Stats Endpoint**: `https://mehajabeen-lunar.hf.space/stats`

### Monitor Session Usage
```bash
# Check active sessions and memory usage
curl https://mehajabeen-lunar.hf.space/stats | jq
```

### Monitor Leaderboard
```bash
# View top 10 performances
curl https://mehajabeen-lunar.hf.space/leaderboard?limit=10 | jq
```

## Troubleshooting

### Issue: "Container not loading" / Timeout
**Causes**: Docker image taking too long to build or start
**Solutions**:
1. Check HF Spaces logs for build errors
2. Verify Docker image builds locally: `docker build -t lunar:test .`
3. Increase health check window in HF Spaces settings

### Issue: "Memory errors" / OOM Kills
**Causes**: Too many sessions accumulating
**Solutions**:
1. Auto-cleanup is enabled (max 100 sessions)
2. Sessions older than 2 hours deleted automatically
3. Monitor `/stats` endpoint for memory usage

### Issue: "Slow response times" / Hanging requests
**Causes**: Session operations taking too long
**Solutions**:
1. Check if environment initialization is issue
2. Verify `SESSION_TIMEOUT` allows long-running tasks (default 60s)
3. Check if too many parallel requests (OS-level connection limit)

### Issue: "API endpoints return 404/500"
**Causes**: Docker container crashed or restarted
**Solutions**:
1. Check HF Spaces build logs
2. Verify all imports in `warehouse_env/server.py`
3. Test locally: `python run_server.py`

## Git Sync with HF Spaces

HF Spaces automatically syncs with GitHub repository:

1. **Enable Auto-Deploy**: Enabled by default
2. **Git Branch**: Syncs from `main` branch
3. **Manual Sync**: Force push if needed: `git push --force`

To manually sync after local changes:
```bash
cd lunar
git add .
git commit -m "Your message"
git push origin main  # Syncs to HF Spaces automatically
```

## Performance Benchmarks (HF Spaces)

| Metric | Value | Status |
|--------|-------|--------|
| Startup Time | ~30s | ✅ Good |
| Health Check | 2s | ✅ Good |
| API Response Time | <1s average | ✅ Good |
| Max Sessions | 100 | ✅ Stable |
| Memory per Session | ~2MB | ✅ Efficient |

## Best Practices

1. **Session Cleanup**: Delete old sessions via DELETE `/sessions/{id}`
2. **Monitor Leaderboard**: Keep top 100 to avoid memory bloat
3. **Test Changes Locally**: Always test Dockerfile changes locally first
4. **Use Health Check**: Regularly ping `/health` to ensure uptime
5. **Version Tags**: Commit semantically (Major.Minor.Patch)

## Advanced Configuration

### Increase Concurrent Sessions
Edit in `session_manager.py`:
```python
# MaxSessions = 100 (default)
# Increase to 200 if needed, monitor memory
manager = SessionManager(max_sessions=200)
```

### Adjust Cleanup Timeout  
Edit in `session_manager.py`:
```python
# session_timeout_hours = 2 (default)
# Increase to 4 for longer tasks
manager = SessionManager(session_timeout_hours=4)
```

### Add Custom Logging
Edit in `run_server.py` - add logging module for debugging HF Spaces logs

## Support

- **GitHub Issues**: Report bugs
- **HF Spaces Logs**: Check for container errors
- **Local Testing**: Replicate issues locally before deploying
