# Contributing to Botty Desktop

## Development setup

```powershell
cd BottyDesktop
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,voice]"
```

Run the desktop smoke and safety tests with:

```powershell
python -m pytest
```

Keep changes focused on the Windows desktop application. Add or update tests
for changed behavior, do not commit local memory, credentials, downloaded
models, or virtual environments, and update the README when installation or
runtime behavior changes.
