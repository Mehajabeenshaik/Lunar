#!/usr/bin/env python
"""
HUGGINGFACE SPACES DEPLOYMENT GUIDE
====================================
Follow these steps EXACTLY to deploy warehouse_env to HF Spaces.
"""

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    HUGGINGFACE SPACES DEPLOYMENT GUIDE                       ║
║                        warehouse_env Project                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

TIME REQUIRED: 30-45 minutes
DEADLINE: April 8, 2026

════════════════════════════════════════════════════════════════════════════════
PREREQUISITES
════════════════════════════════════════════════════════════════════════════════

✓ HuggingFace account (free): https://huggingface.co/join
✓ Git installed on your system
✓ API keys ready:
  - OPENAI_API_KEY (from OpenAI)
  OR
  - HF_TOKEN (from HuggingFace)

════════════════════════════════════════════════════════════════════════════════
STEP 1: CREATE HUGGINGFACE SPACE (5 minutes)
════════════════════════════════════════════════════════════════════════════════

1. Go to: https://huggingface.co/new-space

2. Fill in the form:
   - Space name: warehouse_env
   - License: MIT (or your choice)
   - Select SDK: Docker (not Streamlit)
   - Visibility: Public (or Private)
   - Click "Create space"

3. You'll see a page with:
   - Space URL: https://huggingface.co/spaces/<YOUR_USERNAME>/warehouse_env
   - Clone command (use this next!)

════════════════════════════════════════════════════════════════════════════════
STEP 2: CLONE SPACE REPOSITORY (5 minutes)
════════════════════════════════════════════════════════════════════════════════

In PowerShell, run these commands:

# Create a temporary directory for deployment
mkdir C:\\HF_Deployment
cd C:\\HF_Deployment

# Clone the space repo (replace <YOUR_USERNAME>)
git clone https://huggingface.co/spaces/<YOUR_USERNAME>/warehouse_env
cd warehouse_env

# Configure git (if not already done)
git config user.email "your-email@example.com"
git config user.name "Your Name"

════════════════════════════════════════════════════════════════════════════════
STEP 3: COPY PROJECT FILES (5 minutes)
════════════════════════════════════════════════════════════════════════════════

Copy all files from your local project to the cloned space:

From PowerShell:

# Copy all files from your project
Copy-Item "C:\\Users\\HP\\Documents\\lunar\\warehouse_env\\*" \\.\" -Recurse -Force

# The cloned space directory should now contain:
#   - warehouse_env/
#   - platform/
#   - scripts/
#   - Dockerfile
#   - docker-compose.yml
#   - requirements.txt
#   - openenv.yaml
#   - inference.py
#   - README.md
#   - HF_SPACES_DEPLOYMENT.md
#   - etc.

# Verify files were copied:
ls -la

════════════════════════════════════════════════════════════════════════════════
STEP 4: ADD & COMMIT FILES (5 minutes)
════════════════════════════════════════════════════════════════════════════════

# Stage all files
git add .

# Commit with a meaningful message
git commit -m "Initial warehouse environment deployment - OpenEnv compliant RL environment for inventory optimization"

# Expected output: [main (root-commit) ...] Initial warehouse environment deployment...

════════════════════════════════════════════════════════════════════════════════
STEP 5: PUSH TO HUGGINGFACE (3 minutes)
════════════════════════════════════════════════════════════════════════════════

# Push to the space
git push

# You may be prompted for credentials - use:
# Username: <YOUR_HUGGINGFACE_USERNAME>
# Password: <YOUR_HUGGINGFACE_TOKEN> (from https://huggingface.co/settings/tokens)

════════════════════════════════════════════════════════════════════════════════
STEP 6: ADD SECRETS TO SPACE (5 minutes)
════════════════════════════════════════════════════════════════════════════════

IMPORTANT: This step is REQUIRED for the inference to work!

1. Go to your space: https://huggingface.co/spaces/<YOUR_USERNAME>/warehouse_env

2. Click "Settings" (gear icon, top right)

3. Scroll down to "Repository secrets"

4. Click "Add a secret" and add ONE of the following:

   Option A: OpenAI API Key
   ─────────────────────────
   - Name: OPENAI_API_KEY
   - Value: sk-... (your OpenAI API key)
   - Click "Add secret"

   Option B: HuggingFace Token
   ──────────────────────────
   - Name: HF_TOKEN
   - Value: hf_... (your HF token)
   - Click "Add secret"

   Option C: Both (recommended)
   ───────────────────────────
   - Add both OPENAI_API_KEY and HF_TOKEN

════════════════════════════════════════════════════════════════════════════════
STEP 7: MONITOR BUILD (10-15 minutes)
════════════════════════════════════════════════════════════════════════════════

1. After pushing, HF Spaces automatically builds your Docker image

2. Watch the build progress:
   - Go to your space
   - Click "View logs" or scroll down to see build status
   - Watch for: "Building... Uploading... Running..."

3. Build stages:
   - [1/X] Installing dependencies from requirements.txt
   - [2/X] Copying project files
   - [3/X] Building Docker layers
   - Built successfully ✓

4. When complete, space will be available at:
   https://huggingface.co/spaces/<YOUR_USERNAME>/warehouse_env

Typical duration: 5-15 minutes depending on HF server load

════════════════════════════════════════════════════════════════════════════════
STEP 8: TEST ENDPOINTS (5 minutes)
════════════════════════════════════════════════════════════════════════════════

Once deployed, verify endpoints are working:

# Replace <YOUR_USERNAME> with your actual username

# 1. Health check (should return {"status":"ok"})
curl https://huggingface.co/spaces/<YOUR_USERNAME>/warehouse_env/health

# 2. Reset environment (should return observation)
curl -X POST https://huggingface.co/spaces/<YOUR_USERNAME>/warehouse_env/reset \\
  -H "Content-Type: application/json" \\
  -d '{}'

# 3. Check API docs (interactive Swagger UI)
Visit: https://huggingface.co/spaces/<YOUR_USERNAME>/warehouse_env/docs

════════════════════════════════════════════════════════════════════════════════
STEP 9: FINAL VALIDATION (5 minutes)
════════════════════════════════════════════════════════════════════════════════

Run the validation script (if available in HF Spaces environment):

chmod +x scripts/validate-submission.sh
./scripts/validate-submission.sh \\
  https://huggingface.co/spaces/<YOUR_USERNAME>/warehouse_env \\
  ./

Expected output:
  ✓ Endpoint /health responding
  ✓ Endpoint /reset responsive
  ✓ Task warehouse_easy functional
  ✓ Task warehouse_medium functional
  ✓ Task warehouse_hard functional
  ✓ All validation checks passed

════════════════════════════════════════════════════════════════════════════════
TROUBLESHOOTING
════════════════════════════════════════════════════════════════════════════════

Problem: "Build failed" or "Docker build error"
Solution: 
  - Check requirements.txt for syntax errors
  - Verify Dockerfile exists and is correct
  - Check Space logs for specific error messages
  - Redeploy by pushing again: git push

Problem: "Module not found" or "ImportError"
Solution:
  - Ensure all packages are in requirements.txt
  - Check that warehouse_env/__init__.py exports correct modules
  - Verify relative imports are used (not absolute)

Problem: "API endpoints not responding"
Solution:
  - Wait 5-10 minutes for space to fully initialize
  - Check Space logs for startup errors
  - Verify OPENAI_API_KEY or HF_TOKEN is set
  - Restart the Space (Settings → Restart)

Problem: "Authentication failed" when pushing
Solution:
  - Verify HuggingFace token is correct
  - Regenerate token at: https://huggingface.co/settings/tokens
  - Make sure you have push access to the space

════════════════════════════════════════════════════════════════════════════════
SUCCESS INDICATORS
════════════════════════════════════════════════════════════════════════════════

✓ Your space is deployed when:
  - Build completed successfully (green checkmark)
  - Space shows "Running" status
  - /health endpoint returns {"status":"ok"}
  - /docs page loads (Swagger UI)
  - Can make POST /reset and GET /step requests

════════════════════════════════════════════════════════════════════════════════
POST-DEPLOYMENT CHECKLIST
════════════════════════════════════════════════════════════════════════════════

After deployment, verify:

□ Space URL accessible
□ /health endpoint working
□ /reset endpoint working  
□ /step endpoint working
□ /docs (Swagger UI) loading
□ All 3 tasks functional
□ Inference script running (if testing with LLM)
□ Build logs show no errors
□ Secrets are configured (if using inference)

════════════════════════════════════════════════════════════════════════════════
SUPPORT & DOCUMENTATION
════════════════════════════════════════════════════════════════════════════════

For more information, see:
  - README.md - Full project overview and usage
  - HF_SPACES_DEPLOYMENT.md - Detailed deployment guide
  - HOW_TO_TEST.md - Testing procedures
  - openenv.yaml - Environment specification

════════════════════════════════════════════════════════════════════════════════
DEPLOYMENT COMPLETE!
════════════════════════════════════════════════════════════════════════════════

Your warehouse_env project is now live on HuggingFace Spaces!

Next steps:
  1. Share your space URL with others
  2. Monitor space activity and logs
  3. Update/improve the environment as needed
  4. Use the API for training agents

Thank you for using warehouse_env!
""")
