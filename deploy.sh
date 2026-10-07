#!/bin/bash
# Deploy script: pull code -> install deps -> migrate -> collectstatic -> restart
#
# Order matters: collectstatic must run BEFORE the restart, otherwise the new
# code goes live while the static files are still missing (unstyled pages).
set -e

cd /root/BOT_Django || { echo "[ERROR] Failed to enter project directory"; exit 1; }

# Prefer the project venv, fall back to system python
if [ -x "venv/bin/python" ]; then
    PY="$PWD/venv/bin/python"
    PIP="$PWD/venv/bin/pip"
else
    PY="python"
    PIP="pip"
fi

echo "=========================================="
echo "  BOT_Django Deploy Script"
echo "=========================================="
echo

# -- 1. Pull latest code ----------------------------------------------
if [ -d ".git" ]; then
    echo "[..] Pulling latest code..."
    git pull
    echo "[OK] Code updated"
else
    echo "[WARN] Not a git repository, skip code update"
fi
echo

# -- 2. Install dependencies ------------------------------------------
if [ -f "requirements.txt" ]; then
    echo "[..] Installing dependencies..."
    "$PIP" install -r requirements.txt --quiet
    echo "[OK] Dependencies installed"
    echo
fi

# -- 3. Apply database migrations -------------------------------------
echo "[..] Applying database migrations..."
"$PY" manage.py migrate --noinput
echo "[OK] Migrations applied"
echo

# -- 4. Collect static files ------------------------------------------
# Skipping this leaves pages unstyled: nginx serves /static/ from STATIC_ROOT.
echo "[..] Collecting static files..."
"$PY" manage.py collectstatic --noinput
echo "[OK] Static files collected"
echo

# -- 5. Restart service -----------------------------------------------
echo "[..] Restarting Gunicorn..."
systemctl restart gunicorn

sleep 2
if systemctl is-active --quiet gunicorn; then
    echo "[OK] Service is running"
else
    echo "[ERROR] Service is not running. Check: systemctl status gunicorn -l"
    exit 1
fi

echo
echo "=========================================="
echo "  Deploy Complete!"
echo "=========================================="
