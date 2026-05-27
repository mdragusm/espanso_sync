# Espanso Sync

Cross-platform espanso snippet manager. Edit once, sync everywhere via GitHub.

## What's in this repo

| File | Purpose |
|------|---------|
| `base.yml` | Your espanso snippets |
| `espanso_adder.py` | GUI app to add, edit, and delete snippets |
| `espanso_setup.sh` | Auto-setup script for Linux |
| `setup.ps1` | Auto-setup script for Windows |
| `create_shortcut.ps1` | Creates desktop shortcut on Windows |

---

## Setting up on a new PC

### Linux
Open a terminal and run:
```bash
curl -o setup.sh https://raw.githubusercontent.com/mdragusm/espanso_sync/main/espanso_setup.sh && bash setup.sh
```
Follow the prompts. The only manual step is adding the SSH key to GitHub when it asks.

### Windows
Open PowerShell as Administrator and run:
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
irm https://raw.githubusercontent.com/mdragusm/espanso_sync/main/setup.ps1 | iex
```
Follow the prompts. The only manual step is adding the SSH key to GitHub when it opens the browser.

---

## Daily use

### Adding or editing snippets
- **Linux:** run `espanso-add` in a terminal
- **Windows:** double-click `Espanso Manager` on the desktop

The app lets you add, edit, and delete snippets. It automatically pushes to GitHub and restarts espanso when you're done.

### Syncing manually
If you edited `base.yml` directly and want to push:
```bash
# Linux
espanso-sync

# Windows (in PowerShell)
cd ~/dotfiles
git add base.yml
git commit -m "update snippets"
git push
```

### Getting changes on another PC
Boot the PC — it pulls automatically on login. Or manually:
```bash
cd ~/dotfiles && git pull
```

---

## How it works

```
base.yml in ~/dotfiles  ←──── GitHub repo ────→  base.yml in ~/dotfiles
        ↓                                                  ↓
   symlink                                            symlink
        ↓                                                  ↓
~/.config/espanso/match/base.yml          %APPDATA%\espanso\match\base.yml
        ↓                                                  ↓
     espanso                                            espanso
```

- `base.yml` lives in `~/dotfiles` and is synced via GitHub
- A symlink points espanso to that file instead of its own config folder
- On boot, a systemd service (Linux) or Task Scheduler job (Windows) runs `git pull` to get the latest version
- The GUI app writes directly to `~/dotfiles/base.yml`, pushes to GitHub, and restarts espanso

---

## Snippet format

Snippets in `base.yml` follow this format:
```yaml
matches:
- trigger: triggerword
  replace: the text you want
- trigger: '@pro'
  replace: your@email.com
```

- No quotes needed unless the trigger starts with a special character like `@`
- Triggers are case sensitive
- Espanso detects the trigger as you type and replaces it automatically

---

## Troubleshooting

**Symlink broke (Linux)**
```bash
rm ~/.config/espanso/match/base.yml
ln -s ~/dotfiles/base.yml ~/.config/espanso/match/base.yml
```
The systemd service auto-repairs this on every boot/restart, so it'll fix itself automatically.

**Git push rejected**
Someone pushed changes you don't have locally. Pull first:
```bash
cd ~/dotfiles && git pull
```
Then try again. Avoid editing `base.yml` directly on GitHub to prevent conflicts.

**Snippets not working after editing**
Espanso needs to restart to pick up changes. The app does this automatically, but if needed:
```bash
# Linux
espanso restart

# Windows
espanso restart
```

**Stray characters when a snippet fires**
Make sure `backend: Clipboard` is set in `~/.config/espanso/config/default.yml` (Linux) or `%APPDATA%\espanso\config\default.yml` (Windows).
