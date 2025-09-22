# KolamAI

Interactive Django app to generate, digitize, customize, and manage South Indian Kolam patterns.

## Features
- Generate kolams by grid size and theme (traditional, ocean, sunset, forest, etc.)
- Digitize an uploaded kolam photo into a clean render
- Customize line thickness, dot size, density, symmetry
- Save, list, update, and delete patterns and templates
- Starter gallery via `python manage.py init_templates`

## Architecture
- Backend: Django (views/ORM/templates), SQLite, Pillow, NumPy, OpenCV
- Generator: rule‑based algorithm using a JSON dataset of curve points
- Frontend: single-page template with `fetch()` calls to JSON endpoints

## Setup
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m ensurepip --upgrade   # only if pip is missing
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py init_templates
python manage.py runserver 0.0.0.0:8000
```
Open `http://127.0.0.1:8000/`.

If `Activate.ps1` is blocked:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## API (most used)
- POST `/generate/` → `{ dots, theme }` → base64 image + pattern data
- POST `/digitize/` → form file `kolam_image` → analyzed + digitized images
- GET `/user-patterns/`, POST `/save-pattern/`, `/update-pattern/`, `/delete-pattern/`
- GET `/preferences/`, POST `/update-preferences/`
- GET `/templates/`, POST `/load-template/`

## How it works 
1. UI sends JSON to generate/digitize endpoints
2. Views call the generator or OpenCV pipeline
3. Generator builds a matrix with connectivity + symmetry, maps cells to curve points from `generator_kolam/src/data/kolamPatternsData.json`, and renders PNG with Pillow
4. Response returns base64 image + pattern JSON; some results are saved to SQLite

## Challenges → Solutions
- Technical limits → OpenCV preprocessing (threshold, shadow removal, denoise, perspective fix)
- Accuracy issues → Input validation, show dots/paths; resilient dataset loading with fallback
- Scaling/UX → Vectorized NumPy, optimized 500×500 Pillow renders; clear Windows setup guidance

## Troubleshooting
- Only dots appear → ensure the generator reads `generator_kolam/src/data/kolamPatternsData.json`; restart or hard refresh
- Port busy → `python manage.py runserver 127.0.0.1:8001`
- Pip/venv issues → `python -m ensurepip --upgrade` then reinstall requirements

