param([string]$Name = 'pydml')
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
if ($Name -notmatch '^[A-Za-z0-9_.-]+$') { throw 'Use a simple conda environment name.' }
$taskExisting = conda env list --json | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw 'Could not inspect existing conda environments.' }
if (@($taskExisting.envs | Where-Object { (Split-Path -Leaf $_) -eq $Name }).Count) {
    throw 'That environment already exists. Choose a new name to preserve it.'
}
conda env create --name $Name --file (Join-Path $taskRoot 'environment_dml.yaml')
if ($LASTEXITCODE -ne 0) { throw 'Conda environment creation failed.' }
conda run --name $Name python -m uv pip install --python python -r (Join-Path $taskRoot 'requirements-dml-legacy.txt')
if ($LASTEXITCODE -ne 0) { throw 'DirectML dependencies failed; the environment was retained for diagnosis.' }
conda run --name $Name python -m uv pip check
if ($LASTEXITCODE -ne 0) { throw 'DirectML dependency verification failed.' }
