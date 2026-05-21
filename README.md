# Spotlight Surgeon

Fix macOS Spotlight app search and ghost app entries with a transparent one-file CLI.

Spotlight Surgeon is a small macOS utility for people who search apps from Spotlight and hit weird failures: apps not appearing, duplicate/ghost entries, or stale LaunchServices metadata. It does not delete apps or user files. It shows the exact system commands it will run and supports dry-run mode.

## Install

### Option 1: clone and run

```bash
git clone https://github.com/00xmorty/spotlight-surgeon.git
cd spotlight-surgeon
./spotlight-surgeon doctor --dry-run
```

### Option 2: put it on your PATH

```bash
chmod +x spotlight-surgeon
sudo cp spotlight-surgeon /usr/local/bin/spotlight-surgeon
spotlight-surgeon doctor --dry-run
```

## Usage

```bash
spotlight-surgeon <command> [options]
```

Commands:

- `doctor` — read-only diagnostics: Spotlight status + app search smoke test
- `status` — show Spotlight indexing status
- `apps` — rebuild LaunchServices app registry
- `fix` — ask Spotlight to erase/rebuild the index for `/`
- `verify [AppName]` — check whether Spotlight can find an application
- `help` — show help

Options:

- `--dry-run` — print commands without executing them
- `--yes` / `-y` — skip confirmation prompts for guarded repair commands
- `--verbose` / `-v` — print extra details
- `--version` — print version

## Examples

Start safely:

```bash
./spotlight-surgeon doctor --dry-run
./spotlight-surgeon apps --dry-run
./spotlight-surgeon fix --dry-run
./spotlight-surgeon verify Safari --dry-run
```

If the dry-run output looks right, run the least invasive repair first:

```bash
./spotlight-surgeon apps
```

If Spotlight itself is broken or stale, run the reindex command:

```bash
./spotlight-surgeon fix
```

## What it runs

`status`:

```bash
mdutil -s /
```

`apps`:

```bash
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister \
  -kill -r -domain local -domain system -domain user
```

`fix`:

```bash
mdutil -E /
```

`verify Safari`:

```bash
mdfind "kMDItemKind == 'Application' && kMDItemDisplayName == '*Safari*'"
```

## Safety model

- Does **not** delete apps.
- Does **not** delete user files.
- `doctor`, `status`, and `verify` are read-only diagnostics.
- `apps` rebuilds LaunchServices app registration and asks for confirmation.
- `fix` asks Spotlight to rebuild its index and asks for confirmation.
- `--dry-run` shows the exact command without running it.
- `--yes` exists for automation, but dry-run first is recommended.

## Requirements

- macOS
- zsh
- built-in macOS tools: `mdutil`, `mdfind`, `lsregister`

## Test

```bash
zsh -n spotlight-surgeon
bash tests/smoke.sh
```

## Status

Early MVP. Use `--dry-run` first and open an issue if a command behaves differently on your macOS version.

## License

MIT
