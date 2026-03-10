# Copyright (c) 2026 Yota Yamamoto
# SPDX-License-Identifier: MIT

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$specPath = Join-Path $repoRoot 'Chemease.spec'

function Invoke-PythonModule {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    & python @Arguments
    if ($LASTEXITCODE -ne 0) {
        $joinedArguments = $Arguments -join ' '
        throw ('python ' + $joinedArguments + ' failed.')
    }
}

Push-Location $repoRoot
try {
    $pathsToClean = @(
        'build',
        (Join-Path 'dist' 'Chemease')
    )

    foreach ($relativePath in $pathsToClean) {
        if (Test-Path $relativePath) {
            Remove-Item $relativePath -Recurse -Force
        }
    }

    Invoke-PythonModule -Arguments @('-m', 'pip', 'install', '--upgrade', 'pip')
    Invoke-PythonModule -Arguments @('-m', 'pip', 'install', '-r', 'requirements.txt')
    Invoke-PythonModule -Arguments @('-m', 'pip', 'install', '-r', 'requirements-build.txt')
    Invoke-PythonModule -Arguments @('-m', 'PyInstaller', '--noconfirm', '--clean', $specPath)
}
finally {
    Pop-Location
}
