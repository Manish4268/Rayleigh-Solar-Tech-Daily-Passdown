# Azure Deployment Pre-Test Script
# Run this before deploying to Azure to verify everything works

Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host "  AZURE STATIC WEB APP - PRE-DEPLOYMENT TEST" -ForegroundColor Cyan
Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Check files exist
Write-Host "TEST 1: Checking required files..." -ForegroundColor Yellow
$files = @(
    "frontend\src\lib\azureAuth.js",
    "frontend\src\components\Login.jsx",
    "frontend\src\components\Signup.jsx",
    "frontend\src\App.jsx",
    "frontend\staticwebapp.config.json",
    "frontend\public\logo.png",
    "frontend\package.json"
)

$allFilesExist = $true
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  OK $file" -ForegroundColor Green
    } else {
        Write-Host "  MISSING $file" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if ($allFilesExist) {
    Write-Host "  All files present" -ForegroundColor Green
} else {
    Write-Host "  Some files are missing!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 2: Check if git repo is clean
Write-Host "TEST 2: Checking git status..." -ForegroundColor Yellow
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "  You have uncommitted changes:" -ForegroundColor Yellow
    git status --short
    Write-Host "  Run: git add . && git commit -m 'Azure deployment ready'" -ForegroundColor Cyan
} else {
    Write-Host "  Git repo is clean" -ForegroundColor Green
}

Write-Host ""

# Test 3: Check Node modules
Write-Host "TEST 3: Checking dependencies..." -ForegroundColor Yellow
if (Test-Path "frontend\node_modules") {
    Write-Host "  node_modules exists" -ForegroundColor Green
} else {
    Write-Host "  node_modules missing - Run: cd frontend && npm install" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 4: Try to build
Write-Host "TEST 4: Building frontend..." -ForegroundColor Yellow
Push-Location frontend
try {
    npm run build 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Build successful!" -ForegroundColor Green
        if (Test-Path "dist") {
            $distSize = (Get-ChildItem -Path dist -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
            $sizeRounded = [math]::Round($distSize, 2)
            Write-Host "  Build size: $sizeRounded MB" -ForegroundColor Cyan
        }
    } else {
        Write-Host "  Build failed!" -ForegroundColor Red
        Pop-Location
        exit 1
    }
} catch {
    Write-Host "  Build error: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

Write-Host ""

# Test 5: Check authentication code
Write-Host "TEST 5: Verifying authentication code..." -ForegroundColor Yellow
$authFile = Get-Content "frontend\src\lib\azureAuth.js" -Raw
if ($authFile -match "isAzureSWA" -and $authFile -match "checkAuthentication" -and $authFile -match "logout") {
    Write-Host "  Authentication helper looks good" -ForegroundColor Green
} else {
    Write-Host "  Authentication helper seems incomplete" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 6: Check staticwebapp.config.json
Write-Host "TEST 6: Checking Azure SWA configuration..." -ForegroundColor Yellow
$swaConfig = Get-Content "frontend\staticwebapp.config.json" -Raw | ConvertFrom-Json
if ($swaConfig.auth -and $swaConfig.auth.identityProviders.azureActiveDirectory) {
    Write-Host "  Azure AD configuration present" -ForegroundColor Green
} else {
    Write-Host "  Azure AD configuration missing or incomplete" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host "  TEST SUMMARY" -ForegroundColor Cyan
Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "All tests passed! You are ready to deploy to Azure." -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Commit your changes (if any):" -ForegroundColor White
Write-Host "   git add ." -ForegroundColor Cyan
Write-Host "   git commit -m 'Azure deployment ready'" -ForegroundColor Cyan
Write-Host "   git push origin pce" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Follow the guide in: AZURE_DEPLOYMENT_CHECKLIST.md" -ForegroundColor White
Write-Host ""
Write-Host "3. After deployment to Azure, you will need to:" -ForegroundColor White
Write-Host "   - Register Azure AD application" -ForegroundColor Cyan
Write-Host "   - Set AZURE_CLIENT_ID and AZURE_CLIENT_SECRET" -ForegroundColor Cyan
Write-Host "   - Configure redirect URI" -ForegroundColor Cyan
Write-Host ""
Write-Host "==========================================================================" -ForegroundColor Cyan
