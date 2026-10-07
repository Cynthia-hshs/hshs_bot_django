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

# -- 0. Git LFS preflight ---------------------------------------------
# Game builds (*.wasm / *.data) live in Git LFS. Without git-lfs installed,
# `git pull` writes the 130-byte pointer file as if it were the real content --
# collectstatic copies it happily, nginx returns 200, and the game page is
# blank with no error anywhere. Hard to diagnose, so check BEFORE pulling:
# that way a missing git-lfs aborts while the running site is still intact.
if grep -q 'filter=lfs' .gitattributes 2>/dev/null; then
    if ! command -v git-lfs >/dev/null 2>&1; then
        echo "[ERROR] Repo uses Git LFS but git-lfs is not installed."
        echo "        Install it, then re-run this script."
        echo "        Verify with: git lfs env"
        exit 1
    fi
    # Registers the smudge/clean filters in .git/config so the pull below
    # resolves pointers into real content.
    git lfs install --local >/dev/null
fi

# -- 1. Pull latest code ----------------------------------------------
if [ -d ".git" ]; then
    echo "[..] Pulling latest code..."
    git pull
    echo "[OK] Code updated"
else
    echo "[WARN] Not a git repository, skip code update"
fi
echo

# -- 1.5 Verify LFS content is real, not pointers ----------------------
# `git lfs install` only fixes future checkouts. Files already sitting in the
# working tree as pointers are left alone by `git pull` -- they look unchanged
# to git, so it never re-smudges them. `git lfs pull` does rewrite them.
# Re-check afterwards: deploying pointers is worse than not deploying at all.
# Suffix list must mirror the filter=lfs rules in .gitattributes. Adding a
# suffix there without adding it here means pointers for it slip past this
# check silently -- which is the exact failure this function exists to catch.
lfs_pointers() {
    for f in static/games/*/Build/*.wasm \
             static/games/*/Build/*.data \
             static/games/*/Build/*.unityweb; do
        [ -e "$f" ] || continue
        if head -c 64 "$f" | grep -aq 'git-lfs.github.com'; then
            echo "$f"
        fi
    done
    return 0
}

stale="$(lfs_pointers)"
if [ -n "$stale" ]; then
    echo "[..] Found LFS pointer files, fetching real content..."
    echo "$stale" | sed 's/^/     /'
    git lfs pull
    stale="$(lfs_pointers)"
    if [ -n "$stale" ]; then
        echo "[ERROR] Still pointers after 'git lfs pull':"
        echo "$stale" | sed 's/^/     /'
        echo "        Aborting so we do not ship a blank game page."
        exit 1
    fi
    echo "[OK] LFS content restored"
    echo
fi

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
