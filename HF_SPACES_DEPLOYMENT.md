# HF Spaces Deployment Guide

## Quick Start

### 1. Create HF Space

Visit https://huggingface.co/new-space and create:
- **Space name**: `warehouse_env` (or similar)
- **License**: MIT
- **Space SDK**: Docker
- **Visibility**: Public

### 2. Clone & Push Code

```bash
# Clone your new space
git clone https://huggingface.co/spaces/<your-username>/warehouse_env
cd warehouse_env

# Copy warehouse_env code
# Replace contents with the project files

# Initialize git and push
git add .
git commit -m "Initial warehouse environment setup"
git push
```

### 3. Add Secrets

In Space Settings → Secrets, add:
- `OPENAI_API_KEY`: Your OpenAI API key (sk-...)
- `HF_TOKEN`: Your HuggingFace API token
- `API_BASE_URL` (optional): Custom LLM endpoint
- `MODEL_NAME` (optional): Model to use (default: gpt-4-turbo)

### 4. Wait for Build

Space will automatically build Docker image and deploy. Check build logs in Space Settings.

## Project Structure for HF Spaces

```
warehouse_env/
├── Dockerfile              # Required: builds container
├── requirements.txt        # Dependencies
├── pyproject.toml         # Python package config
├── setup.py               # Python build info
├── openenv.yaml           # OpenEnv spec metadata
├── README.md              # Main documentation
├── inference.py           # Baseline inference script (required in root)
├── app.py                 # HF Spaces entry point
├── docker-compose.yml     # Local testing
├── warehouse_env/
│   ├── __init__.py
│   ├── __main__.py
│   ├── models.py          # Pydantic type models
│   ├── env.py             # Environment logic
│   ├── server.py          # FastAPI server
│   └── graders.py         # Task graders
├── scripts/
│   └── validate-submission.sh
└── .gitignore
```

## Testing Locally Before Deploy

### With Docker

```bash
# Build image
docker build -t warehouse-env:latest .

# Run container (set env vars)
docker run -p 5000:5000 \
  -e OPENAI_API_KEY=sk-... \
  -e MODEL_NAME=gpt-4-turbo \
  warehouse-env:latest

# Test endpoint
curl http://localhost:5000/health
```

### With Docker Compose

```bash
# Create .env file with secrets
cat > .env << EOF
OPENAI_API_KEY=sk-...
HF_TOKEN=...
MODEL_NAME=gpt-4-turbo
WAREHOUSE_TASK=warehouse_easy
EOF

# Start (builds if needed)
docker-compose up

# Test in another terminal
curl http://localhost:5000/health
```

### Without Docker (Direct Python)

```bash
# Install
pip install -e .

# Set environment
export OPENAI_API_KEY=sk-...
export MODEL_NAME=gpt-4-turbo

# Run server
python -m warehouse_env.server

# Test
curl http://localhost:5000/health
```

## API Endpoints

All endpoints available at `https://<your-space>.hf.space/`:

### POST /reset
Reset environment to initial state.

Request:
```json
{"task": "warehouse_easy"}
```

Response:
```json
{
  "observation": {...},
  "task": "warehouse_easy"
}
```

### POST /step
Execute one step with action.

Request:
```json
{
  "action": {
    "reorder_quantities": [100.0],
    "transfers": [[0.0]]
  }
}
```

Response:
```json
{
  "observation": {...},
  "reward": 0.75,
  "done": false,
  "info": {"service_level": 0.95}
}
```

### GET /state
Get current environment state.

Response:
```json
{
  "state": {...},
  "task": "warehouse_easy",
  "episode_rewards": [0.75, 0.78, ...]
}
```

### GET /render
Get text rendering of environment.

### GET /health
Health check (used for validation).

Response:
```json
{"status": "ok"}
```

## Running Inference

After Space is deployed, run baseline:

```bash
export OPENAI_API_KEY=sk-...
export WAREHOUSE_TASK=warehouse_easy
python inference.py
```

Expected output format:
```
[START] task=warehouse_easy env=warehouse_env model=gpt-4-turbo
[STEP] step=1 action=reorder([50.0]) reward=0.75 done=false error=null
[STEP] step=2 action=reorder([55.0]) reward=0.78 done=false error=null
...
[END] success=true steps=8 score=0.71 rewards=0.75,0.78,...
```

## Pre-Submission Checklist

- [ ] Dockerfile builds without error
- [ ] `docker run` starts and responds to /health
- [ ] openenv.yaml exists and is valid
- [ ] inference.py in root directory
- [ ] Produces structured logs: [START], [STEP], [END]
- [ ] All 3 tasks have graders
- [ ] Graders return scores in [0.0, 1.0]
- [ ] README.md is comprehensive
- [ ] HF Space URL is public
- [ ] Space responds to ping with 200

## Validation

Run validator before submitting:

```bash
chmod +x scripts/validate-submission.sh
./scripts/validate-submission.sh https://<your-space>.hf.space ./
```

## Troubleshooting

### Container won't start
- Check Docker logs: `docker-compose logs warehouse-env`
- Verify requirements.txt is correct
- Check Dockerfile syntax

### API not responding
- Verify PORT is set to 5000
- Check firewall: `curl http://localhost:5000/health`
- Review app.py entry point

### Inference times out
- Increase MAX_STEPS timeout if needed
- Check API_BASE_URL is reachable
- Verify OPENAI_API_KEY is valid

### Scores not in [0, 1]
- Check grader logic in graders.py
- Verify reward calculation in env.py
- Test locally first

## Support

- OpenEnv Docs: https://docs.openenv.dev
- HF Spaces Docs: https://huggingface.co/docs/hub/spaces
- FastAPI Docs: https://fastapi.tiangolo.com/
