# Setup Instructions

## Prerequisites
- Python 3.8+

## Install & Run
`ash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
`

The app runs at http://127.0.0.1:8000/
