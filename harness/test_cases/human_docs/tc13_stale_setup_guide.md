# Getting Started: Project Setup Guide

Welcome to the WidgetFactory project! Follow these steps to get your development environment running.

## Prerequisites

- Git 2.30+
- A GitHub account with access to the `widgetfactory` org

## Step 1: Clone the Repository

```bash
git clone git@github.com:widgetfactory/backend.git
cd backend
```

## Step 2: Install Python

Install Python 3.8:

```bash
brew install python@3.8
```

Verify the installation:

```bash
python3 --version  # Should show 3.8.x
```

## Step 3: Install Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install flask-auth
```

## Step 4: Configure the Database

```bash
cp .env.example .env
# Edit .env with your local database credentials
python3 manage.py migrate
```

## Step 5: Run the Development Server

```bash
python3 manage.py runserver
```

The app will be available at http://localhost:8000.

## Troubleshooting

If you encounter SSL errors, try:

```bash
brew install openssl
export LDFLAGS="-L/opt/homebrew/lib"
```
