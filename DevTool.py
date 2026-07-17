#!/usr/bin/env python3
"""
devtools.py — N8's Video To Gifski build tool
----------------------------------------
Usage:
    python devtools.py          # build with auto-incremented count
    python devtools.py --dry    # preview version string, don't build
    python devtools.py --reset  # reset build counter to 0
    python devtools.py --dmg    # build DMG after building the app
"""

import subprocess
import sys
import os
import re
import json
import argparse
import shutil
from datetime import datetime
from pathlib import Path

from modules.platformModules import mac, win

# ── Config ────────────────────────────────────────────────────────────────────

SPEC_FILE = "N8VideoToGifski.spec"
VERSION_FILE = Path("__version__.py")
BUILD_FILE = Path("build_count.json")  # readable by the GUI too
DIST_DIR = Path("dist")
ROOT_DIR = Path(".")
APP = "N8's Video To Gifski"
EXT = ".app" if mac else ".exe"

FINAL_DMG_NAME = "N8's Video To Gifski Installer"
FINAL_DMG_FILE = f"{FINAL_DMG_NAME}.dmg"
pre_existing_final_dmg = ROOT_DIR / FINAL_DMG_FILE

# Signing — switch to "Developer ID Application: ..." when notarizing
SIGNING_IDENTITY = "Developer ID Application: John Nathaniel Calvara (C9MNV8M79M)"
ENTITLEMENTS_FILE = Path("entitlements.plist")

# Set to True when switching to Developer ID for notarization.
# Adds --timestamp to the codesign command (required by Apple for notarization,
# but causes errSecInternalComponent with Apple Development certs during long builds).
IS_DIST_BUILD = False

# Dylibs shipped by PaddlePaddle with SDK version (0,0,0) — invalid for
# hardened-runtime signing. Must be re-signed individually after the build.
RESIGN_DYLIBS = [
    "libblas.dylib",
    "liblapack.dylib",
]


# ── Build Icons ───────────────────────────────────────────────────────────────────
def build_icons():
    from tools.icnsBuilder import pngtoicns, pngtoico

    if mac:
        ICONS_DIR = "./buildandsign/icons/MacOS/"
        pngtoicns(f"{ICONS_DIR}icon.png", ICONS_DIR)
        pngtoicns(f"{ICONS_DIR}icoDMG.png", ICONS_DIR)
        print("  ✓ Mac Icons built using tools/icnsBuilder.py")
    if win:
        ICONS_DIR = "./buildandsign/icons/Windows/"
        pngtoico(f"{ICONS_DIR}icon.png", ICONS_DIR)
        print("  ✓ Windows Icons built using tools/icnsBuilder.py")


# ── Build JSON ────────────────────────────────────────────────────────────────


def read_build_file() -> dict:
    if BUILD_FILE.exists():
        try:
            return json.loads(BUILD_FILE.read_text())
        except (json.JSONDecodeError, KeyError):
            pass
    return {"build_count": 0}


def write_build_file(data: dict):
    BUILD_FILE.write_text(json.dumps(data, indent=4))


def bump_build_count() -> int:
    data = read_build_file()
    data["build_count"] = data.get("build_count", 0) + 1
    write_build_file(data)
    return data["build_count"]


def save_build_info(count: int, base_version: str, label: str, now: datetime):
    """
    Writes the full build record to build_count.json.
    The GUI reads this file directly — no string parsing needed.
    """
    data = {
        "build_count": count,
        "build_label": label,
        "base_version": base_version,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
    }
    write_build_file(data)


# ── Version helpers ───────────────────────────────────────────────────────────


def read_base_version() -> str:
    """Reads __version__ from __version__.py without importing it."""
    text = VERSION_FILE.read_text()
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', text, re.MULTILINE)
    if not match:
        raise ValueError(f"Could not parse __version__ from {VERSION_FILE}")
    return match.group(1)


def make_build_label(base_version: str, count: int, now: datetime) -> str:
    """
    Produces a label like:  0.0.4a-B47.202606041423
    Format: {base_version}-B{count}.{YYYYMMDD}{HHMM}
    """
    date_part = now.strftime("%Y%m%d")
    time_part = now.strftime("%H%M")
    return f"{base_version}-B{count}.{date_part}{time_part}"


def update_changelog():
    if mac:
        subprocess.run(["git-cliff", "-o", "CHANGELOG.md"])
        print("  ✓ CHANGELOG.md updated using git-cliff")


# ── Pre-build checks ──────────────────────────────────────────────────────────


def check_prerequisites():
    errors = []

    if not Path(SPEC_FILE).exists():
        errors.append(f"Spec file not found: {SPEC_FILE}")

    if not VERSION_FILE.exists():
        errors.append(f"Version file not found: {VERSION_FILE}")

    if shutil.which("pyinstaller") is None:
        errors.append("pyinstaller not found in PATH — is your venv active?")

    if errors:
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)


# ── Build ─────────────────────────────────────────────────────────────────────


def run_pyinstaller(build_label: str) -> int:
    env = os.environ.copy()
    env["BUILD_VERSION"] = build_label  # spec reads via os.environ.get()

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        SPEC_FILE,
    ]

    print(f"\n  Running: {' '.join(cmd)}")
    print(f"  BUILD_VERSION = {build_label}\n")
    print("─" * 60)

    result = subprocess.run(cmd, env=env)
    return result.returncode


# ── Post-build ────────────────────────────────────────────────────────────────


def post_build_summary(build_label: str, count: int, success: bool):
    print("\n" + "─" * 60)
    app_path = DIST_DIR / f"{APP}{EXT}"

    if success:
        if app_path.is_dir():
            size_mb = sum(f.stat().st_size for f in app_path.rglob("*") if f.is_file()) / 1_048_576
        elif app_path.is_file():
            size_mb = app_path.stat().st_size / 1_048_576
        else:
            size_mb = 0

        print(f"  ✓ Build complete")
        print(f"    Label   : {build_label}")
        print(f"    Count   : {count}")
        print(f"    Output  : {app_path}")
        print(f"    Size    : {size_mb:.1f} MB")
    else:
        print(f"  ✗ Build FAILED  (label: {build_label})")
        print(f"    build_count.json was already updated — decrement manually if needed")


# ── Post-build SSL dylib conflict fix ────────────────────────────────────────


def fix_ssl_dylib_conflict(app_path: Path):
    """
    Replace cv2's libssl/libcrypto symlinks with the correct Homebrew versions.

    What happens without this:
      - cv2 ships its own older libssl.3.dylib (pre-OpenSSL 3.3, missing
        SSL_SESSION_get_time_ex).
      - PyInstaller creates Contents/Frameworks/libssl.3.dylib as a symlink
        pointing to cv2/.dylibs/libssl.3.dylib.
      - Python's _ssl.cpython-313-darwin.so loads that symlink at runtime,
        gets the wrong version, and crashes with "Symbol not found".

    What this does:
      - Replaces those top-level symlinks with the REAL Homebrew OpenSSL files
        that _ssl was compiled against.
      - cv2's own copies stay untouched in cv2/.dylibs/ for cv2's internal use.
      - Both cv2 (via libsrt) and _ssl end up using the Homebrew version,
        which is compatible with both.
    """
    frameworks = app_path / "Contents" / "Frameworks"

    brew_root = Path("/opt/homebrew/opt/openssl@3/lib")
    ssl_libs = ["libssl.3.dylib", "libcrypto.3.dylib"]

    print("Fixing OpenSSL dylib conflict (cv2 vs Python _ssl)...")

    if not brew_root.exists():
        print(f"    ✗  Homebrew openssl@3 not found at {brew_root}")
        print(f"       Run: brew install openssl@3")
        return

    for name in ssl_libs:
        src = brew_root / name
        dest = frameworks / name

        if not src.exists():
            print(f"    ⚠  {name} not found in Homebrew — skipping")
            continue

        if dest.is_symlink():
            old_target = os.readlink(dest)
            dest.unlink()
            shutil.copy2(src, dest)
            print(f"    ✓  {name}: symlink ({old_target}) → Homebrew real file")
        elif dest.exists():
            dest.unlink()
            shutil.copy2(src, dest)
            print(f"    ✓  {name}: replaced with Homebrew version")
        else:
            shutil.copy2(src, dest)
            print(f"    ✓  {name}: added Homebrew version")


# ── Post-build signing ────────────────────────────────────────────────────────


def sign_app(app_path: Path):
    """
    Sign the .app bundle after PyInstaller build.

    PyInstaller's internal signing always adds --timestamp, which contacts
    Apple's timestamp server and requires the Keychain to stay unlocked for
    the entire build. With Apple Development certificates this causes
    errSecInternalComponent during long builds (Keychain auto-locks, or
    timestamp server request fails mid-build).

    By setting codesign_identity=None in the spec, PyInstaller builds unsigned
    and we own the entire signing pass here with full control over flags.

    Signing order matters on macOS:
      1. Patch individual dylibs that have invalid SDK versions (PaddlePaddle)
      2. Deep-sign the whole bundle (re-signs everything consistently)
    """
    print("\n  Signing app bundle...")

    # ── Step 1: Patch known-bad paddle dylibs (SDK version 0,0,0)
    # These must be signed individually before the bundle pass because
    # codesign --deep would fail on them without a prior fix.
    print("  Patching paddle dylibs with invalid SDK version...")
    patched = 0
    for name in RESIGN_DYLIBS:
        matches = list(app_path.rglob(name))
        if not matches:
            print(f"    ⚠  Not found: {name} (skipping)")
            continue
        for dylib in matches:
            result = subprocess.run(
                ["codesign", "--force", "--sign", SIGNING_IDENTITY, str(dylib)],
                capture_output=True,
                text=True,
            )
            rel = dylib.relative_to(app_path)
            if result.returncode == 0:
                print(f"    ✓  {rel}")
                patched += 1
            else:
                print(f"    ✗  {rel}: {result.stderr.strip()}")

    # ── Step 2: Sign the whole bundle
    print(f"\n  Deep-signing bundle ({patched} dylib(s) pre-patched)...")
    cmd = [
        "codesign",
        "--force",
        "--deep",
        "--sign",
        SIGNING_IDENTITY,
        "--options",
        "runtime",
        # --timestamp is intentionally omitted for Apple Development certificates.
        # Add it (and switch SIGNING_IDENTITY) when building for notarization:
        #   "--timestamp",
    ]
    if ENTITLEMENTS_FILE.exists():
        cmd += ["--entitlements", str(ENTITLEMENTS_FILE)]
    if IS_DIST_BUILD:
        cmd.append("--timestamp")
    cmd.append(str(app_path))

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ✓  Bundle signed")
    else:
        print(f"  ✗  Bundle signing failed:")
        print(f"     {result.stderr.strip()}")


def notarize_and_staple(target_path: Path):
    """
    Submit a signed .app (zipped) or .dmg to Apple's notary service, wait
    for the result, then staple the ticket so Gatekeeper works offline.
    """
    submit_path = target_path
    if target_path.suffix == ".app":
        submit_path = target_path.with_suffix(".zip")
        subprocess.run(["ditto", "-c", "-k", "--keepParent", str(target_path), str(submit_path)])

    print(f"\n  Submitting {submit_path.name} to Apple notary service...")
    result = subprocess.run(
        [
            "xcrun",
            "notarytool",
            "submit",
            str(submit_path),
            "--keychain-profile",
            "n8ventures-notary",  # see setup note below
            "--wait",
        ],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0 or "status: Accepted" not in result.stdout:
        print(f"  ✗ Notarization failed:\n{result.stderr}")
        return False

    print(f"  Stapling ticket to {target_path.name}...")
    subprocess.run(["xcrun", "stapler", "staple", str(target_path)])
    return True


# Note: Run this command first
# xcrun notarytool store-credentials "n8ventures-notary" \
#   --apple-id "n8ventures@gmail.com" \
#   --team-id "28N6MRL39U" \
#   --password "<app-specific password from appleid.apple.com>"


#  BUILD DMG
def build_dmg(app_name="N8's Video to Gifski"):
    """
    Build DMG by calling dmgbuild's Python API directly.

    The subprocess approach fails with "Unable to detach device cleanly" because
    capture_output=True pipes stdio, which interferes with hdiutil's disk
    management when detaching the temporary mount. Calling the API directly
    runs in the same process context and avoids this entirely.
    """

    try:
        import dmgbuild as _dmgbuild
    except ImportError:
        print("  ✗ dmgbuild not installed — run: pip install dmgbuild")
        return

    app_src = (DIST_DIR / f"{app_name}.app").resolve()
    dmg_out = (DIST_DIR / f"{app_name}.dmg").resolve()

    if dmg_out.exists():
        dmg_out.unlink()

    print(f"  Building DMG from {app_src.name}...")
    _dmgbuild.build_dmg(
        filename=str(dmg_out),
        volume_name=app_name,
        settings_file="dmg_settings.py",
        defines={"app": str(app_src)},  # absolute path → no move-to-root needed
        detach_retries=10,  # extra retries in case Spotlight is busy
    )
    print(f"  ✓ DMG built: {dmg_out}")

    if dmg_out.exists():
        dmg_out.rename(DIST_DIR / FINAL_DMG_FILE)
    else:
        print(f"  DMG not found after build: {dmg_out}")
        print("Obviously, dmgbuild still doesn't move it to the dist folder. Assuming it's in root...")

        root_dmg = ROOT_DIR / f"{app_name}.dmg"

        if pre_existing_final_dmg.exists():
            print(f"  Found pre-existing DMG in root: {pre_existing_final_dmg}")
            print(f"  Deleting pre-existing DMG...")
            pre_existing_final_dmg.unlink()

        if root_dmg.exists():
            print(f"  Found DMG in root: {root_dmg}")
            root_dmg.rename(pre_existing_final_dmg)

            try:
                print(f"  Setting DMG icon using 'fileicon'...")
                subprocess.run(
                    [
                        "fileicon",
                        "set",
                        str(pre_existing_final_dmg),
                        "buildandsign/icons/MacOS/icoDMG.icns",
                    ],
                    check=True,
                )
            except Exception as e:
                print(f"  ✗ Failed to set DMG icon: {e}")
                print("  Please ensure 'fileicon' is installed and available in PATH.")
                print("  You can install it via Homebrew: brew install fileicon")
        else:
            print(f"  DMG not found in root either: {root_dmg}")
            print("  Please check the dmgbuild output for errors.")
            return


# ── CLI ───────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Video To Gifski build tool")
    parser.add_argument("--dry", action="store_true", help="Preview version, skip build")
    parser.add_argument("--reset", action="store_true", help="Reset build counter to 0")
    parser.add_argument("--count", type=int, help="Override build count (doesn't save)")
    parser.add_argument("--dmg", action="store_true", help="Build DMG after building the app")
    args = parser.parse_args()

    update_changelog()
    build_icons()

    if args.dmg:
        build_dmg()
        return

    # ── Reset
    if args.reset:
        write_build_file({"build_count": 0})
        print(f"  ✓ Build counter reset to 0")
        return

    check_prerequisites()

    base_version = read_base_version()
    now = datetime.now()

    # ── Dry run
    if args.dry:
        next_count = read_build_file().get("build_count", 0) + 1
        label = make_build_label(base_version, next_count, now)
        print(f"\n  Dry run — next build would be:")
        print(f"    Base version : {base_version}")
        print(f"    Build count  : {next_count}")
        print(f"    Full label   : {label}")
        print(f"    Date / Time  : {now.strftime('%Y-%m-%d')} {now.strftime('%H:%M')}")
        print(f"\n  (build_count.json not modified)\n")
        return

    # ── Real build
    if args.count is not None:
        count = args.count
    else:
        count = bump_build_count()

    # If version is bumped, reset Build count.
    if base_version != read_build_file().get("base_version", ""):
        count = 1

    label = make_build_label(base_version, count, now)

    # Write the full record now — GUI can read this even from inside the app
    save_build_info(count, base_version, label, now)

    print(f"\n  N8's {APP} — {label}")
    print("─" * 60)
    if win:
        from tools.generateRC import genMainRC
        from __version__ import __version__

        genMainRC(__version__, APP)
        print(f"  ✓ .rc built!")

    returncode = run_pyinstaller(label)
    post_build_summary(label, count, success=(returncode == 0))

    if returncode == 0:
        app_path = DIST_DIR / f"{APP}{EXT}"

        if mac:
            fix_ssl_dylib_conflict(app_path)
            sign_app(app_path)

            if IS_DIST_BUILD:
                notarize_and_staple(app_path)

            build_dmg()

            version = read_base_version()
            FINAL_DMG_FILE_name = f"{FINAL_DMG_NAME}-{version}"

            try:
                print("  Checking if existing dmgs and zips are in Dist folder...")
                dmg_in_dist = DIST_DIR / pre_existing_final_dmg
                dmg_zip_in_dist = DIST_DIR / f"{FINAL_DMG_FILE_name}.zip"
                dmg_in_dist.unlink(missing_ok=True)
                dmg_zip_in_dist.unlink(missing_ok=True)
            except Exception as e:
                print(f"  ✗ Failed to delete dmgs: {e}")

            try:
                shutil.move(pre_existing_final_dmg, DIST_DIR)
                print("  Moved DMG to dist folder.")
            except Exception as e:
                print(f"  ✗ Failed to Move DMG to dist folder: {e}")

            dmg_path = DIST_DIR / f"{FINAL_DMG_NAME}.dmg"
            if IS_DIST_BUILD:
                subprocess.run(["codesign", "--force", "--sign", SIGNING_IDENTITY, "--timestamp", str(dmg_path)])
                notarize_and_staple(dmg_path)

            zip_output = DIST_DIR / f"{FINAL_DMG_FILE_name}.zip"
            subprocess.run(["ditto", "-c", "-k", "--keepParent", str(dmg_path), str(zip_output)])
            print("  ✓ Zipped final signed/notarized/stapled DMG")

    sys.exit(returncode)


if __name__ == "__main__":
    main()
