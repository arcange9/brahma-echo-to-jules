# Brahma Echo — Playwright Browser Setup
# This script downloads Chromium for Playwright if not already present.
# Run after installation or on first launch via PowerShell.

$ErrorActionPreference = "Stop"

Write-Host "============================================"
Write-Host "  Brahma Echo - Playwright Browser Setup"
Write-Host "============================================"
Write-Host ""

$PlaywrightDir = "$env:LOCALAPPDATA\ms-playwright"
$BrowserFound = $false

# Check if playwright browsers are already installed
if (Test-Path $PlaywrightDir) {
    $chromiumDirs = Get-ChildItem -Path $PlaywrightDir -Directory -Filter "chromium-*" -ErrorAction SilentlyContinue
    if ($chromiumDirs) {
        $BrowserFound = $true
        Write-Host "Playwright Chromium is already installed."
        Write-Host "Location: $PlaywrightDir"
    }
}

if (-not $BrowserFound) {
    Write-Host ""
    Write-Host "Playwright Chromium browser not found."
    Write-Host ""
    Write-Host "Brahma Echo uses Playwright for browser automation features."
    Write-Host "To enable these features, install the Chromium browser:"
    Write-Host ""
    Write-Host "Option 1: Using pip (if Python is available)"
    Write-Host "  pip install playwright"
    Write-Host "  playwright install chromium"
    Write-Host ""
    Write-Host "Option 2: Using the bundled installer"
    Write-Host "  Run this PowerShell script as administrator"
    Write-Host ""
    Write-Host "Note: Other Brahma Echo features work without the browser."
    Write-Host ""

    # Try to install chromium automatically if python/playwright is available
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        Write-Host "Attempting automatic Chromium download..."
        try {
            & python -m playwright install chromium 2>&1
            Write-Host "Chromium download complete."
        } catch {
            Write-Host "Automatic download failed. Please install manually."
            Write-Host $_.Exception.Message
        }
    } else {
        Write-Host "Python not found on PATH. Manual installation required."
    }
}

Write-Host ""
Write-Host "Browser setup check complete."
Write-Host ""
