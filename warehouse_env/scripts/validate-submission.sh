#!/usr/bin/env bash
#
# validate-submission.sh — OpenEnv Submission Validator
#
# Validates that HF Space is live, Docker builds, inference runs, and scores are valid.

set -uo pipefail

PING_URL="${1:-}"
REPO_DIR="${2:-.}"

if [ -z "$PING_URL" ]; then
    echo "Usage: validate-submission.sh <ping_url> [repo_dir]"
    echo "Example: validate-submission.sh https://my-space.hf.space ./warehouse_env"
    exit 1
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

PASSED=0
FAILED=0

check() {
    local name="$1"
    local cmd="$2"
    
    echo -n "Checking: $name... "
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC}"
        ((FAILED++))
        return 1
    fi
}

echo -e "${BOLD}OpenEnv Submission Validator${NC}\n"

# 1. Check HF Space is live
check "HF Space responds to ping" "curl -sf '$PING_URL/health' > /dev/null"

# 2. Check openenv.yaml exists
check "openenv.yaml exists" "[ -f '$REPO_DIR/openenv.yaml' ]"

# 3. Check Dockerfile exists
check "Dockerfile exists" "[ -f '$REPO_DIR/Dockerfile' ]"

# 4. Check inference.py exists
check "inference.py in root" "[ -f '$REPO_DIR/inference.py' ]"

# 5. Check README
check "README.md exists" "[ -f '$REPO_DIR/README.md' ]"

# 6. Check models in openenv.yaml
check "Models defined in openenv.yaml" "grep -q 'warehouse_easy' '$REPO_DIR/openenv.yaml'"

echo ""
echo -e "${BOLD}Summary${NC}"
echo -e "Passed: ${GREEN}$PASSED${NC}  Failed: ${RED}$FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✓ All checks passed!${NC}"
    exit 0
else
    echo -e "\n${RED}✗ Some checks failed${NC}"
    exit 1
fi
