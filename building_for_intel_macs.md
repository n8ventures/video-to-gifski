# Building an x86_64 (Intel) Python on Apple Silicon via Rosetta

A from-scratch guide to getting a genuinely x86_64 CPython build working on an
M-series Mac, for producing an Intel-compatible build of an app (e.g. via
PyInstaller) without owning physical Intel hardware.

This exists because every step of this process has a non-obvious failure
mode. Each section below is a real wall we hit, in the order we hit it, with
the *why* — not just the fix — so future-you (or anyone else using this)
understands what's actually happening instead of cargo-culting commands.

---

## The core idea

Apple Silicon Macs can run x86_64 code via **Rosetta 2** translation. If you
run an entire build toolchain (Homebrew, Python's own build system,
`pip`, PyInstaller) *inside a Rosetta-translated process*, everything they
produce comes out x86_64 — including a Python interpreter you can then use
to build genuinely Intel-compatible wheels and, eventually, an Intel-native
`.app`/executable.

The tricky part: multiple independent layers of your system have to *all*
agree they're "being x86_64" at the same time — your shell, Homebrew, the
compiler's default target — and Apple's tooling doesn't always propagate
that agreement automatically. Most of the pain below comes from one layer
correctly being x86_64 while another silently defaults back to native arm64.

---

## 1. Install Rosetta 2 (if not already present)

```bash
softwareupdate --install-rosetta
```

Usually already installed if you've ever run any Intel-only app, but worth
running explicitly first.

---

## 2. Install a separate, Intel-only Homebrew

Apple Silicon Homebrew lives at `/opt/homebrew`. Intel Homebrew needs its own
separate install at `/usr/local` — they're designed to coexist without
conflicting.

**Gotcha #1 — sudo prompt fails under `NONINTERACTIVE=1`:**

```bash
NONINTERACTIVE=1 arch -x86_64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# ==> Checking for `sudo` access...
# Need sudo access on macOS...
```

`NONINTERACTIVE=1` disables *all* prompts, including the one that would
normally ask for your password mid-install. Without a cached sudo
credential, the installer's non-interactive sudo check just fails — and
running the whole thing under plain `sudo` doesn't work either (`Don't run
this as root!`, since Homebrew explicitly refuses to install as root).

**Fix:** prime the sudo cache yourself first, then run the installer:

```bash
sudo -v
NONINTERACTIVE=1 arch -x86_64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Does this overwrite your existing arm64 Homebrew?** No — the install
script detects its own running architecture (`arm64` vs `x86_64`, itself
translated correctly by Rosetta) and picks the prefix accordingly:
`/opt/homebrew` when run natively, `/usr/local` when run under
`arch -x86_64`. They don't collide. Only watch for: the installer may add a
second `brew shellenv` line to `~/.zprofile` — check it afterward so your
*default* (non-Rosetta) terminal sessions don't accidentally start resolving
`brew`/`python` to the Intel copies.

**Gotcha #2 — permission errors on `/usr/local/share/...`:**

```
Error: The following directories are not writable by your user:
/usr/local/share/zsh
/usr/local/share/zsh/site-functions
```

Pre-existing macOS system directories under `/usr/local/share` can be
root-owned on a fresh machine. Fix by taking ownership (Homebrew tells you
the exact command, but the broader-strokes version, since it tends to recur
one subdirectory at a time):

```bash
sudo chown -R $(whoami) /usr/local/share
```

---

## 3. Install build dependencies under Intel Homebrew

```bash
arch -x86_64 zsh                         # open a translated shell first
/usr/local/bin/brew install tcl-tk openssl@3 readline sqlite3 xz zlib pkg-config
```

`pkg-config` matters — CPython's `configure` script uses it to locate
Tcl/Tk. If it's missing from the Intel prefix, `configure` silently falls
back to whatever `pkg-config` it finds elsewhere on `$PATH` — almost
certainly your arm64 one at `/opt/homebrew/bin/pkg-config` — which then
reports paths/flags for the *wrong* architecture's libraries.

**Note on Tcl/Tk 9:** as of mid-2026, Homebrew's `tcl-tk` formula installs
**9.0.x**, not the long-standing 8.6 line. If you hardcode
`-ltcl8.6 -ltk8.6` anywhere (e.g. in `PYTHON_CONFIGURE_OPTS`), it'll silently
fail to link. Check what's actually installed before assuming:

```bash
/usr/local/bin/brew info tcl-tk
```

---

## 4. Get `pyenv` to build a *separate* x86_64 Python, without clobbering your existing arm64 one

`pyenv` identifies versions purely by version string (`3.14.6`) — it has no
concept of architecture. If you already have an arm64 `3.14.6` installed and
try to `pyenv install 3.14.6` again under Rosetta, it just asks "already
exists, reinstall?" — accepting risks silently overwriting your working
arm64 environment under the same name.

**Fix — temporarily move the existing version aside, install fresh, rename,
restore:**

```bash
mv ~/.pyenv/versions/3.14.6 ~/.pyenv/versions/3.14.6-arm64-backup
pyenv install 3.14.6              # builds under Rosetta, lands as plain "3.14.6"
mv ~/.pyenv/versions/3.14.6 ~/.pyenv/versions/3.14.6_x86
mv ~/.pyenv/versions/3.14.6-arm64-backup ~/.pyenv/versions/3.14.6
```

(An earlier attempt to call `python-build` directly with an explicit output
directory — the "textbook" way to sidestep this — failed because this
particular `pyenv` install [via Homebrew] doesn't vendor `python-build` at
the path most guides assume. The move-aside approach works regardless of
how `pyenv` itself is installed, since it just uses `pyenv install`
normally.)

---

## 5. Point the build at the Intel libraries — and *only* those

```bash
export PATH="/usr/local/bin:$PATH"
export PKG_CONFIG="/usr/local/bin/pkg-config"
export PKG_CONFIG_PATH="/usr/local/opt/tcl-tk/lib/pkgconfig:/usr/local/opt/openssl@3/lib/pkgconfig:/usr/local/opt/sqlite/lib/pkgconfig:/usr/local/opt/zlib/lib/pkgconfig"
export CFLAGS="-arch x86_64"
export LDFLAGS="-arch x86_64 -L/usr/local/opt/tcl-tk/lib -L/usr/local/opt/openssl@3/lib -L/usr/local/opt/sqlite/lib -L/usr/local/opt/zlib/lib"
export CPPFLAGS="-I/usr/local/opt/tcl-tk/include -I/usr/local/opt/openssl@3/include -I/usr/local/opt/sqlite/include -I/usr/local/opt/zlib/include"
```

Notes:

- **`readline` is deliberately excluded.** It's only needed for interactive
  REPL line-editing (arrow keys, history at a `>>>` prompt) — irrelevant to
  a frozen GUI app with no interactive Python prompt. Trying to link it
  turned into its own multi-hour rabbit hole (see Gotcha #3 below) for zero
  practical benefit. `configure` gracefully skips building the `readline`
  module when it's not found — no error, just `checking for readline... no`.
- `readline`, `sqlite`, and `zlib` from Homebrew are **keg-only** (not
  symlinked into `/usr/local/lib` directly, since macOS ships its own older
  versions) — that's *why* they need explicit `-L`/`-I` paths at all,
  instead of "just working" once installed.
- **`CFLAGS="-arch x86_64"` is the single most important line here** — see
  Gotcha #4, it's the thing that actually made everything else work.

**Gotcha #3 — readline links against the wrong library, fails with a cryptic
symbol error:**

```
[ERROR] readline failed to import: dlopen(...readline.cpython-314-darwin.so...):
symbol not found in flat namespace '_rl_catch_signals'
```

This is *not* an architecture mismatch (both the built module and Homebrew's
readline were confirmed x86_64 via `file`). `_rl_catch_signals` is a
GNU-readline-internal symbol; macOS ships its own `/usr/lib/libreadline.dylib`,
which is actually BSD `libedit` wearing readline's name for legacy
compatibility, and doesn't implement that symbol. Something in the dyld
resolution chain preferred the system shim over the real Homebrew readline.
**Resolution: don't fight it — just don't build the module at all** (see
above). It cost real time before we realized it was a non-problem for a
frozen GUI app.

**Gotcha #4 (the big one) — `arch -x86_64 zsh` doesn't make `clang` emit
x86_64 by default:**

Even with `sysctl -n sysctl.proc_translated` correctly reporting `1`
(confirming the *shell itself* is genuinely running translated), a plain
`clang test.c -o test` still produced an **arm64** binary. Symptom in a real
build: OpenSSL's `.dylib`s are confirmed x86_64 via `file`, but `configure`'s
link test fails with:

```
ld: warning: ignoring file '.../libcrypto.dylib': found architecture 'x86_64', required architecture 'arm64'
Undefined symbols for architecture arm64: ...
```

**Why:** `arch -x86_64` controls which slice of a universal binary *runs* —
it does correctly make the shell process itself translated. But Apple's
`clang` driver picks its *default compilation target* by querying the
underlying hardware directly, a query Apple deliberately lets see through
Rosetta translation (so software can still detect "this is really Apple
Silicon" even while running under emulation). So `clang` runs as genuine
x86_64 code, and still defaults to *emitting* arm64 machine code — those are
two separate things, and only the first one is what `arch -x86_64` actually
governs.

**Fix:** never rely on the ambient default — force it explicitly via
`CFLAGS`/`LDFLAGS` (not `CPPFLAGS`, since `-arch` isn't a preprocessor flag):

```bash
export CFLAGS="-arch x86_64"
export LDFLAGS="-arch x86_64 ...(existing -L flags)..."
```

**Verify before running a 10+ minute build, every time you open a new
session:**

```bash
sysctl -n sysctl.proc_translated        # must be 1
echo 'int main(){return 0;}' > /tmp/archtest.c
clang -arch x86_64 /tmp/archtest.c -o /tmp/archtest
file /tmp/archtest                      # must say x86_64
```

If you skip `-arch x86_64` on the `clang` test line above, it may well come
back `arm64` even with a correctly Rosetta-translated shell — that gap *is*
the bug this whole section is about.

---

## 6. Build

```bash
rm -rf ~/.pyenv/versions/3.14.6_x86     # if retrying — a failed pyenv install auto-deletes its own target dir, but doesn't hurt to be explicit
pyenv install 3.14.6
```

`pyenv install` failing mid-build **automatically deletes the destination
directory** it was installing into (`~/.pyenv/versions/<version>`) — this is
intentional (a half-built interpreter missing critical modules is worse than
none at all), not data loss. The actual build *log* and temp source tree
survive at the path printed in the failure message
(`/var/folders/.../python-build.<timestamp>.<pid>/`) — that's where to look
for real errors, not the destination folder.

---

## 7. Verify the result

```bash
~/.pyenv/versions/3.14.6_x86/bin/python3.14 -c "
import ssl, sqlite3, zlib, tkinter
print('ssl, sqlite3, zlib, tkinter all OK')
"
file ~/.pyenv/versions/3.14.6_x86/bin/python3.14   # should say x86_64
```

`readline` will correctly `ModuleNotFoundError` — that's expected and fine
per the decision above, not a build defect.

---

## 8. Create the Intel venv and install app dependencies

```bash
~/.pyenv/versions/3.14.6_x86/bin/python3.14 -m venv .venv-intel
source .venv-intel/bin/activate
pip install -r requirements.txt
```

`pip` resolves wheels based on the *running interpreter's* platform tag —
under this x86_64 interpreter it'll correctly fetch x86_64 wheels for
everything automatically, no manual wheel-hunting needed.

---

## 9. Build with PyInstaller, sign, verify

```bash
pyinstaller YourApp.spec
codesign --force --deep --sign - "dist/YourApp.app"
file "dist/YourApp.app/Contents/MacOS/YourApp"    # confirm x86_64
```

Also swap any bundled external binaries (ffmpeg, gifski, etc.) for their
x86_64 builds separately — those come from wherever you source them
directly, not from `pip`, so the interpreter architecture doesn't touch
them at all.

---

## Quick troubleshooting index

| Symptom | Likely cause | Section |
|---|---|---|
| `pyenv: already exists` on install | Version-string collision with existing arm64 build | §4 |
| `Need sudo access` under `NONINTERACTIVE=1` | No cached sudo credential | §2 Gotcha #1 |
| `directories are not writable` during `brew install` | Root-owned `/usr/local/share/...` on fresh install | §2 Gotcha #2 |
| `checking for pkg-config... /opt/homebrew/bin/pkg-config` in configure log | `pkg-config` missing from Intel Homebrew, falling back to arm64 one | §3 |
| `_rl_catch_signals` symbol not found (readline) | macOS's fake libedit-based readline shim getting linked instead of real GNU readline | §5 Gotcha #3 — just skip readline |
| `found architecture 'x86_64', required architecture 'arm64'` during OpenSSL/any link test | `clang` defaulting to native arm64 output despite a correctly Rosetta-translated shell | §5 Gotcha #4 — add `-arch x86_64` to `CFLAGS`/`LDFLAGS` |
| Destination folder vanished after a failed `pyenv install` | Expected — pyenv auto-cleans failed installs | §6 |