# QUICKSTART.md

Welcome to **envguard**! This guide will get you up and running in 5 minutes.

## Installation

```bash
# Navigate to the project directory
cd /home/prabhath/Documents/projects/envguard

# Create and activate virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install envguard in development mode
pip install -e .
```

## Basic Usage

### 1. Try with Examples

```bash
# Go to examples directory
cd examples/

# Validate the example .env file
envguard check

# Audit for security issues
envguard audit

# Show differences
envguard diff
```

### 2. Initialize Your Own Schema

```bash
# Create your .env file
cat > .env << 'EOF'
DATABASE_URL=postgresql://localhost:5432/mydb
API_KEY=changeme
DEBUG=true
PORT=8000
EOF

# Generate schema from your .env
envguard init

# This creates .env.schema.toml - now customize it!
```

### 3. Validate and Audit

```bash
# Validate your configuration
envguard check

# Find security issues
envguard audit

# Compare env vs schema
envguard diff
```

## JSON Output for CI/CD

```bash
# All commands support --json flag
envguard check --json
envguard audit --json
envguard diff --json
```

## Exit Codes

Commands return proper exit codes for automation:

- **0** - Success
- **1** - Validation/audit failed
- **2** - Error (file not found, parse error, etc.)

## Example CI/CD Usage

```bash
#!/bin/bash
# In your CI pipeline

# Validate environment configuration
envguard check --env .env.example --json

if [ $? -ne 0 ]; then
    echo "Environment validation failed!"
    exit 1
fi

# Audit for security issues
envguard audit --env .env.example --json

if [ $? -ne 0 ]; then
    echo "Security issues detected!"
    exit 1
fi

echo "All checks passed!"
```

## Common Commands

```bash
# Auto-detect and validate
envguard check

# Specify files explicitly
envguard check --env .env.production --schema .env.prod.schema.toml

# Audit only (no schema needed)
envguard audit

# Show diff
envguard diff

# Create schema from existing .env
envguard init

# Get help
envguard --help
envguard check --help
```

## Next Steps

1. Read [README.md](README.md) for detailed documentation
2. Check [DEVELOPMENT.md](DEVELOPMENT.md) for development setup
3. Explore [examples/](examples/) directory
4. Write tests for your use case
5. Customize the schema format validators in [envguard/validator.py](envguard/validator.py)

## Need Help?

- Check the examples in `examples/`
- Read the full documentation in `README.md`
- Look at test files in `tests/` for usage patterns
- Review the code - it's well-documented!

Happy validating! 🛡️
