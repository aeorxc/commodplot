# commodplot

Common plotting and HTML-report helpers for commodity analytics. The package
supports Python 3.9 and newer and includes its Jinja templates and CSS in built
distributions.

## Install as a library

```powershell
python -m pip install commodplot
```

## Development with uv

Development and CI use `uv` 0.11.28 and the committed `uv.lock`. The private
Oil feed is the only package index; its upstream supplies public dependencies.
Authenticate without putting credentials in project files:

```powershell
foreach ($name in "UV_INDEX", "UV_INDEX_URL", "UV_EXTRA_INDEX_URL", "UV_NO_INDEX", "UV_OFFLINE") {
    if (Test-Path "Env:$name") { Remove-Item "Env:$name" }
}
$pat = [Uri]::EscapeDataString($env:AZURE_DEVOPS_EXT_PAT)
$env:UV_DEFAULT_INDEX = "https://ado:${pat}@pkgs.dev.azure.com/RWEST-MFI-TE/_packaging/Oil_Feed/pypi/simple/"
$env:UV_INDEX_STRATEGY = "first-index"
```

Azure Pipelines sets the equivalent authenticated `UV_DEFAULT_INDEX` through
`PipAuthenticate`. The credential-free feed URL is what is recorded in the
lock file.

Create or update the local `.venv` with the complete development environment:

```powershell
uv --no-config sync --locked
```

Run the test and coverage workflow:

```powershell
uv --no-config run --locked pytest --numprocesses 2 `
  --cov=commodplot --cov-report=term-missing --cov-report=xml tests
```

The Azure pipeline installs only the `test` dependency group. To reproduce
that smaller environment locally:

```powershell
uv --no-config sync --locked --no-default-groups --group test
uv --no-config run --locked --no-sync pytest --numprocesses 2 `
  --cov=commodplot --cov-report=term-missing --cov-report=xml tests
```

## Updating dependencies

Change dependency declarations in `pyproject.toml`, then regenerate and verify
the lock with the pinned uv version:

```powershell
uv --no-config lock
uv --no-config lock --check
uv --no-config sync --locked
```

Using `--no-config` and clearing ambient index variables prevents a user-level
`uv.toml` or shell profile from introducing a second registry into the lock.

Do not add credentials or credential-bearing index URLs to `pyproject.toml` or
`uv.lock`. `requirements.txt` and `requirements-test.txt` remain temporarily
for the repository's tracked GitHub Actions workflows. Azure Pipelines uses the
locked pyproject groups; migrate GitHub Actions separately once authenticated
Oil_Feed access is configured for those runners.

## Build

```powershell
uv --no-config build
```
