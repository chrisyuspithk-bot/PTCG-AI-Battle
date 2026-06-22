# Pull the four official kiyotah rule-based sample kernels (requires .kaggle/kaggle.json).
# Run from repo root:
#   powershell -File scripts/fetch_official_rule_samples.ps1
#
# If PowerShell chokes on this file, use:
#   scripts/fetch_official_rule_samples.cmd

$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)

if (-not (Test-Path '.kaggle\kaggle.json')) {
    Write-Error 'Missing .kaggle/kaggle.json - configure Kaggle API credentials first.'
}

$python = 'C:\Users\tobin\AppData\Local\Programs\Python\Python313\python.exe'
if (-not (Test-Path $python)) {
    $python = 'python'
}

$kernels = @(
    @{ Name = 'sample_lucario'; Kernel = 'kiyotah/a-sample-rule-based-agent-mega-lucario-ex-deck' },
    @{ Name = 'sample_abomasnow'; Kernel = 'kiyotah/a-sample-rule-based-agent-mega-abomasnow-ex-deck' },
    @{ Name = 'sample_dragapult'; Kernel = 'kiyotah/a-sample-rule-based-agent-dragapult-ex-deck' },
    @{ Name = 'sample_iono'; Kernel = 'kiyotah/a-sample-rule-based-agent-iono-s-deck' }
)

foreach ($k in $kernels) {
    $dest = "notebooks\official\$($k.Name)"
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    Write-Host "Fetching $($k.Kernel) -> $dest"
    & $python -m kaggle kernels pull $k.Kernel -p $dest --metadata
}

Write-Host ''
Write-Host 'Done. Next:'
Write-Host '  python scripts/extract_public_agents.py'
Write-Host '  python scripts/bootstrap_official_rule_agents.py'
