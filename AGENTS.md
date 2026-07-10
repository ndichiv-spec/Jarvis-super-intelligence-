# Jarvis - Developer Agent Knowledge

## Test Commands

### Cloud Platform (`packages/cloud/`)
```powershell
cd packages/cloud
$env:PYTHONPATH = "src"; uv run --no-project pytest tests/ -v
```

### Enterprise Platform (`packages/enterprise/`)
```powershell
cd packages/enterprise
$env:PYTHONPATH = "src"; uv run --no-project pytest tests/ -v
```
