# 🚀 Quick Start - Push Backend to GitHub

## Step 1: Open PowerShell
```powershell
cd d:\erp-love\storeflow-erp\backend
```

## Step 2: Initialize Git (if needed)
```powershell
git init
```

## Step 3: Check What Will Be Uploaded
```powershell
git status
```
**✅ You should NOT see:** `.env`, `venv/`, `db.sqlite3`

## Step 4: Add & Commit
```powershell
git add .
git commit -m "Initial backend for VPS deployment"
```

## Step 5: Create GitHub Repo
1. Go to https://github.com/new
2. Name: `storeflow-backend`
3. Click "Create Repository"

## Step 6: Push to GitHub
```powershell
git remote add origin https://github.com/YOUR-USERNAME/storeflow-backend.git
git branch -M main
git push -u origin main
```

---

## ❌ What NOT to Upload
- `.env` (secrets)
- `venv/` (virtual environment)
- `db.sqlite3` (database)
- `__pycache__/` (cache)
- Electron folder
- node_modules/

## ✅ What TO Upload
- All `.py` files
- `requirements.txt`
- `.env.example`
- `manage.py`
- Django folders

---

## 📖 Full Guide
See `vps_deployment_guide.md` for complete VPS setup instructions.
