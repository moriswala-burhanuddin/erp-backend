# StoreFlow Backend - GitHub Push Script
# Run this from PowerShell to push your backend to GitHub

Write-Host "🚀 StoreFlow Backend - GitHub Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to backend directory
Set-Location "d:\erp-love\storeflow-erp\backend"

# Check if .env is properly ignored
Write-Host "🔍 Checking for sensitive files..." -ForegroundColor Yellow
$status = git status --porcelain

if ($status -match "\.env$" -or $status -match "venv/" -or $status -match "db\.sqlite3") {
    Write-Host "⚠️  WARNING: Sensitive files detected!" -ForegroundColor Red
    Write-Host "The following should NOT be uploaded:" -ForegroundColor Red
    Write-Host "  - .env (contains secrets)" -ForegroundColor Red
    Write-Host "  - venv/ (virtual environment)" -ForegroundColor Red
    Write-Host "  - db.sqlite3 (database)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check your .gitignore file!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ No sensitive files detected" -ForegroundColor Green
Write-Host ""

# Show what will be uploaded
Write-Host "📦 Files to be uploaded:" -ForegroundColor Yellow
git status --short
Write-Host ""

# Confirm with user
$confirm = Read-Host "Do you want to continue? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "❌ Cancelled" -ForegroundColor Red
    exit 0
}

# Add all files
Write-Host ""
Write-Host "📝 Adding files..." -ForegroundColor Yellow
git add .

# Commit
$commitMessage = Read-Host "Enter commit message (or press Enter for default)"
if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    $commitMessage = "Backend deployment - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
}

git commit -m $commitMessage

# Check if remote exists
$remoteExists = git remote | Select-String -Pattern "origin"

if (-not $remoteExists) {
    Write-Host ""
    Write-Host "⚠️  No GitHub remote found!" -ForegroundColor Yellow
    Write-Host "Please create a GitHub repository first:" -ForegroundColor Yellow
    Write-Host "1. Go to https://github.com/new" -ForegroundColor Cyan
    Write-Host "2. Name it: storeflow-backend" -ForegroundColor Cyan
    Write-Host "3. Click 'Create Repository'" -ForegroundColor Cyan
    Write-Host ""
    
    $repoUrl = Read-Host "Enter your GitHub repository URL (e.g., https://github.com/username/storeflow-backend.git)"
    
    git remote add origin $repoUrl
    git branch -M main
}

# Push to GitHub
Write-Host ""
Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Yellow
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📖 Next Steps:" -ForegroundColor Cyan
    Write-Host "1. SSH into your VPS" -ForegroundColor White
    Write-Host "2. Follow the instructions in vps_deployment_guide.md" -ForegroundColor White
    Write-Host "3. Clone your repository on the VPS" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ Push failed!" -ForegroundColor Red
    Write-Host "Please check your GitHub credentials and try again." -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
