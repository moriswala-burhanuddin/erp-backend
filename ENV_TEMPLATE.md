# 📝 Quick Reference - .env File for VPS

Copy and paste this into your VPS `.env` file:

```bash
# Django Settings
SECRET_KEY=django-insecure-v^im=muzn-5z#%iim9-pyzfk_%)3=4d-y6g*f7sw$d)a=z71$+
DEBUG=False
ALLOWED_HOSTS=YOUR_VPS_IP_HERE

# Database (PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=storeflow_db
DB_USER=postgres
DB_PASSWORD=admin
DB_HOST=localhost
DB_PORT=5432

# CORS Settings
CORS_ALLOW_ALL_ORIGINS=True
```

---

## 🔧 What to Change

1. **ALLOWED_HOSTS** - Replace `YOUR_VPS_IP_HERE` with your actual VPS IP
   - Example: `ALLOWED_HOSTS=123.45.67.89`
   - With domain: `ALLOWED_HOSTS=123.45.67.89,yourdomain.com`

2. **DB_PASSWORD** - Change `admin` to a strong password
   - Example: `DB_PASSWORD=MyStr0ng!Pass2024`

3. **SECRET_KEY** (Optional but recommended for production)
   - Generate new: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

---

## 📍 How to Edit on VPS

```bash
nano .env
```

1. Paste the content above
2. Edit the values (use arrow keys)
3. Save: `Ctrl+X`, then `Y`, then `Enter`
