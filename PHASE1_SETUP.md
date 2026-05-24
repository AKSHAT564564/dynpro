# Phase 1: Project Setup & Core Infrastructure

## Overview

This guide walks through setting up the project and verifying Phase 1 is complete.

**Duration**: ~30 minutes  
**Goal**: Have a working FastAPI project with core configuration and utilities

---

## Step 1: Create Virtual Environment

```bash
# Navigate to project directory
cd /Users/akshat/Desktop/projects/dynpro

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

Verify activation (you should see `(venv)` in your terminal):
```bash
which python
# Should show: /Users/akshat/Desktop/projects/dynpro/venv/bin/python
```

---

## Step 2: Upgrade pip

```bash
pip install --upgrade pip setuptools wheel
```

---

## Step 3: Install Project Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Verify installation
pip list | head -20
```

Expected packages (top of list):
- fastapi
- uvicorn
- pydantic
- langgraph
- litellm
- httpx
- structlog

---

## Step 4: Create .env File

```bash
# Copy template
cp .env.example .env

# Edit with your settings (for now, just basic settings)
nano .env  # or your preferred editor
```

**Minimum settings for Phase 1:**
```env
ENVIRONMENT=development
LOG_LEVEL=INFO
API_PORT=8000
OUTPUT_DIR=./output
```

**LLM credentials** (optional for Phase 1, required for Phase 5):
```env
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

---

## Step 5: Create Output Directory

```bash
mkdir -p output
chmod 755 output
```

---

## Step 6: Verify Project Structure

Check that all expected files exist:

```bash
# Check main files
ls -la | grep -E "requirements|\.env|\.gitignore|pyproject"

# Check src structure
find src -type f -name "*.py" | sort

# Expected structure:
# src/__init__.py
# src/config.py
# src/models.py
# src/utils/__init__.py
# src/utils/logging.py
# src/fastapi_app/__init__.py
# src/mcp_integration/__init__.py
# src/agents/__init__.py
# src/resource_storage/__init__.py
# src/output_generation/__init__.py
# src/litellm_integration/__init__.py
```

---

## Step 7: Run Unit Tests

```bash
# Run Phase 1 tests
pytest tests/test_config.py -v

# Expected output:
# test_settings_creation PASSED
# test_get_settings PASSED
# test_settings_debug_flag PASSED
```

---

## Step 8: Test Configuration Loading

Create a quick test script:

```bash
cat > test_phase1.py << 'EOF'
#!/usr/bin/env python3
"""Quick Phase 1 verification script"""

import sys
from src.config import get_settings
from src.utils.logging import setup_logging, get_logger

# Setup logging
setup_logging("DEBUG")
logger = get_logger(__name__)

# Test settings
try:
    settings = get_settings()
    logger.info("✓ Settings loaded successfully")
    logger.info(f"  - App Name: {settings.APP_NAME}")
    logger.info(f"  - Environment: {settings.ENVIRONMENT}")
    logger.info(f"  - Debug: {settings.DEBUG}")
    logger.info(f"  - API Port: {settings.API_PORT}")
    logger.info(f"  - Output Dir: {settings.OUTPUT_DIR}")
except Exception as e:
    logger.error(f"✗ Failed to load settings: {e}")
    sys.exit(1)

# Test logging
try:
    logger.info("✓ Logging configured successfully")
    logger.debug("This is a debug message")
    logger.warning("This is a warning message")
except Exception as e:
    logger.error(f"✗ Failed to initialize logger: {e}")
    sys.exit(1)

logger.info("✓ All Phase 1 checks passed!")
EOF

python3 test_phase1.py
```

Expected output (in JSON format):
```json
{"event": "✓ Settings loaded successfully", ...}
{"event": "  - App Name: Context-Aware Question Generator", ...}
{"event": "  - Environment: development", ...}
{"event": "✓ Logging configured successfully", ...}
{"event": "✓ All Phase 1 checks passed!", ...}
```

Clean up:
```bash
rm test_phase1.py
```

---

## Step 9: Verify Models

```bash
# Test that models can be imported and instantiated
python3 << 'EOF'
from src.models import AnalysisState, AnalysisRequest, AnalysisResponse
from datetime import datetime

# Create test instances
state = AnalysisState(
    transcript_text="Test transcript",
    one_pager_text="Test proposal",
    execution_start_time=datetime.now()
)

request = AnalysisRequest(jira_id="TEST-123")

response = AnalysisResponse(
    status="success",
    output_path="./output/TEST-123/",
    artifacts={"questions": "path"},
    execution_time=10.5,
    jira_id="TEST-123"
)

print("✓ All models created successfully")
print(f"  - AnalysisState: {state.transcript_text[:20]}...")
print(f"  - AnalysisRequest: {request.jira_id}")
print(f"  - AnalysisResponse: {response.status}")
EOF
```

Expected output:
```
✓ All models created successfully
  - AnalysisState: Test transcript...
  - AnalysisRequest: TEST-123
  - AnalysisResponse: success
```

---

## Phase 1 Checklist

- [ ] Virtual environment created and activated
- [ ] Dependencies installed via `pip install -r requirements.txt`
- [ ] `.env` file created from `.env.example` with basic settings
- [ ] `output/` directory created
- [ ] All source files in correct locations (`src/config.py`, `src/models.py`, etc.)
- [ ] Unit tests pass: `pytest tests/test_config.py -v`
- [ ] Settings can be loaded: `python3 -c "from src.config import get_settings; print(get_settings().APP_NAME)"`
- [ ] Logging works: Test script passes
- [ ] All models can be instantiated
- [ ] Git repository is ready (`.gitignore` in place)

---

## What's Ready

After Phase 1, you have:

✅ **Project Structure**
- Organized source code in `src/`
- Separate modules for each concern
- Package structure for importing

✅ **Configuration Management**
- Environment-based settings in `src/config.py`
- Support for `.env` file with template
- Type-safe settings with Pydantic

✅ **Logging**
- Structured logging with structlog
- JSON-formatted output
- Configurable log levels

✅ **Data Models**
- Pydantic models for type safety
- Request/response models for API
- AnalysisState for workflow

✅ **Development Tools**
- `pyproject.toml` for project metadata
- `pytest` for unit testing
- Git-ready with `.gitignore`

---

## Next Steps

Ready to move to Phase 2? Check:

```bash
# Verify everything before Phase 2
python3 -c "
from src.config import get_settings
from src.models import AnalysisState
from src.utils.logging import get_logger

print('✓ All imports work')
print('✓ Ready for Phase 2: MCP Integration Framework')
"
```

If you see no errors, you're ready for **Phase 2: MCP Integration Framework**!

---

## Troubleshooting

### Import errors
```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### .env not loading
```bash
# Verify .env exists in project root
ls -la .env

# Verify PYTHONPATH includes project root
echo $PYTHONPATH
# Should include current directory, if empty:
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Tests failing
```bash
# Run tests with verbose output
pytest tests/ -vv -s

# Check Python version (need 3.10+)
python3 --version
```

### Virtual environment issues
```bash
# Deactivate and remove old venv
deactivate
rm -rf venv

# Create fresh venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Success Indicator

When you see this output, Phase 1 is complete:

```
✓ All imports work
✓ Settings loaded
✓ Models instantiate
✓ Tests passing
✓ Ready for Phase 2
```

