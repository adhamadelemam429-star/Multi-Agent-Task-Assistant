# Development Guide

## Local setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run the API

```powershell
uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000
```

## Run the UI

```powershell
streamlit run app.py
```

## Run tests

```powershell
python -m pytest -q
```

## Useful notes

- This project uses Demo Mode by default.
- The database is created automatically in the local storage folder.
- Keep uploads under the configured limits for safe local behavior.
