param(
    [int]$WaitForPid = 0,
    [string]$Python = "C:\Users\tobin\AppData\Local\Programs\Python\Python313\python.exe",
    [string]$RunId = ""
)

$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..")

if ([string]::IsNullOrWhiteSpace($RunId)) {
    $RunId = Get-Date -Format "yyyyMMdd_HHmmss"
}

$OutDir = "report\background_runs\deep_slate_validation_$RunId"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$Log = Join-Path $OutDir "run.log"

function Write-Log {
    param([string]$Message)
    $line = "[$(Get-Date -Format o)] $Message"
    Add-Content -Path $Log -Value $line -Encoding UTF8
}

function Run-Step {
    param(
        [string]$Name,
        [string[]]$Args,
        [string]$StdoutFile
    )
    Write-Log "START $Name"
    Write-Log ("CMD " + $Python + " " + ($Args -join " "))
    & $Python @Args *> $StdoutFile
    $code = $LASTEXITCODE
    Write-Log "END $Name exit=$code output=$StdoutFile"
    if ($code -ne 0) {
        throw "$Name failed with exit code $code"
    }
}

Write-Log "Deep slate validation started in $PWD"

if ($WaitForPid -gt 0) {
    $proc = Get-Process -Id $WaitForPid -ErrorAction SilentlyContinue
    if ($proc) {
        Write-Log "Waiting for existing process PID $WaitForPid ($($proc.ProcessName)) before starting validation"
        Wait-Process -Id $WaitForPid
        Write-Log "Waited process PID $WaitForPid finished"
    } else {
        Write-Log "WaitForPid $WaitForPid was not running; continuing"
    }
}

$deckList = @(
    "agent_decks/deck_rl/gen19_fast_basic.csv",
    "agent_decks/top_mined_trevenant.csv",
    "agent_decks/real_mega_lucario_ex.csv",
    "agent_decks/a2_kyogre_33_energy.csv"
) -join ","

Run-Step `
    -Name "robust_pool_g24_search" `
    -Args @(
        "scripts/evaluate_robust_deck_pool.py",
        "--games", "24",
        "--workers", "1",
        "--scorer", "search",
        "--decks", $deckList,
        "--output", (Join-Path $OutDir "robust_pool_g24_search")
    ) `
    -StdoutFile (Join-Path $OutDir "robust_pool_g24_search.stdout.txt")

$candidates = @(
    "dist/candidates/track_a_lucario_search.tar.gz",
    "dist/candidates/track_a_gen19_fast_basic_search.tar.gz",
    "dist/candidates/track_a_trevenant_leader_search.tar.gz",
    "dist/candidates/track_b_learned_gen19_fast_basic.tar.gz",
    "dist/candidates/track_a_kyogre_search_backup.tar.gz"
)

foreach ($candidate in $candidates) {
    $name = [System.IO.Path]::GetFileNameWithoutExtension([System.IO.Path]::GetFileNameWithoutExtension($candidate))
    Run-Step `
        -Name "public_gate_g30_$name" `
        -Args @(
            "scripts/gate_vs_public.py",
            "--agent", $candidate,
            "--games", "30"
        ) `
        -StdoutFile (Join-Path $OutDir "public_gate_g30_$name.txt")
}

Write-Log "Deep slate validation complete"
