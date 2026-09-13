#!/usr/bin/env python3
"""
QQ Music macOS Decryptor (qqmusic_decrypt_mac)
Decrypts .mflac, .mgg, .mflac0, .mgg1 audio files downloaded from QQ Music for Mac.
"""

import argparse
import glob
import hashlib
import os
import platform
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Optional


def caesar_cipher(text: str, shift: int) -> str:
    res = []
    for c in text:
        if "A" <= c <= "Z":
            res.append(chr((ord(c) - ord("A") + shift) % 26 + ord("A")))
        elif "a" <= c <= "z":
            res.append(chr((ord(c) - ord("a") + shift) % 26 + ord("a")))
        elif "0" <= c <= "9":
            res.append(chr((ord(c) - ord("0") + shift) % 10 + ord("0")))
        else:
            res.append(c)
    return "".join(res)


def get_qqmusic_udid() -> str:
    plist_candidates = [
        Path.home() / "Library/Preferences/com.tencent.QQMusicMac.plist",
        Path.home() / "Library/Containers/com.tencent.QQMusicMac/Data/Library/Preferences/com.tencent.QQMusicMac.plist",
    ]
    pattern = re.compile(b'_\\x10\\(([0-9a-f]{40})')

    for p in plist_candidates:
        if p.exists():
            try:
                data = p.read_bytes()
                match = pattern.search(data)
                if match:
                    return match.group(1).decode("ascii")
            except Exception as e:
                continue

    raise RuntimeError(
        "Could not find QQMusicMac UDID in plist preferences.\n"
        "Make sure QQ Music Mac has been launched and logged in at least once."
    )


def get_mmkv_configs(udid: str) -> List[Tuple[str, str, str]]:
    idata_dir = (
        Path.home()
        / "Library/Containers/com.tencent.QQMusicMac/Data/Library/Application Support/QQMusicMac/iData"
    )

    if not idata_dir.exists():
        raise RuntimeError(f"QQMusicMac iData directory not found at: {idata_dir}")

    configs = []
    for i in range(10):
        str1 = caesar_cipher(udid, i + 3)
        int1 = int(udid[5:7], 16)
        int2 = 5 + (int1 + i) % 4
        name = str1[:int2]
        int3 = i + 0xa546
        str3 = f"{udid}{int3:04x}"
        key = hashlib.md5(str3.encode()).hexdigest()[:16]
        db_path = idata_dir / name
        if db_path.exists():
            configs.append((str(db_path), key, name))

    # Prioritize 240112 (id=1, standard QQMusic Mac audio key store)
    configs.sort(key=lambda x: 0 if x[2] == "240112" else 1)
    return configs


def get_engine_binary() -> Path:
    base_dir = Path(__file__).parent.resolve()
    arch = platform.machine().lower()

    if arch in ("arm64", "aarch64"):
        candidate = base_dir / "bin" / "um_arm64"
    else:
        candidate = base_dir / "bin" / "um_x86_64"

    if candidate.exists() and os.access(candidate, os.X_OK):
        return candidate

    # Fallback checks
    for alt in [base_dir / "bin" / "um", base_dir / "bin" / "um_arm64", base_dir / "bin" / "um_x86_64"]:
        if alt.exists() and os.access(alt, os.X_OK):
            return alt

    raise FileNotFoundError(f"Unlock engine binary not found in {base_dir / 'bin'}")


def decrypt_file(
    engine: Path,
    file_path: Path,
    output_dir: Path,
    mmkv_configs: List[Tuple[str, str, str]],
    overwrite: bool = True,
) -> bool:
    for db_path, key, name in mmkv_configs:
        cmd = [
            str(engine),
            "--qmc-mmkv", db_path,
            "--qmc-mmkv-key", key,
            "-i", str(file_path),
            "-o", str(output_dir),
        ]
        if overwrite:
            cmd.append("--overwrite")

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Decrypt QQ Music macOS encrypted audio files (.mflac, .mgg, .mflac0, .mgg1)."
    )
    parser.add_argument(
        "-i", "--input",
        type=str,
        default=None,
        help="Input file or directory (default: QQMusicMac iQmc download folder)",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="./output",
        help="Output directory (default: ./output)",
    )
    parser.add_argument(
        "--delete-source",
        action="store_true",
        help="Delete encrypted source file after successful decryption",
    )
    parser.add_argument(
        "--no-overwrite",
        action="store_true",
        help="Do not overwrite existing decrypted files",
    )

    args = parser.parse_args()

    default_dir = (
        Path.home()
        / "Library/Containers/com.tencent.QQMusicMac/Data/Library/Application Support/QQMusicMac/iQmc"
    )

    target_path = Path(args.input).expanduser().resolve() if args.input else default_dir
    output_dir = Path(args.output).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if not target_path.exists():
        sys.exit(f"[!] Error: Target path does not exist: {target_path}")

    # Gather files
    supported_exts = {".mflac", ".mgg", ".mflac0", ".mgg1", ".mflaca", ".mflach", ".mflacl", ".mflacm"}
    if target_path.is_file():
        files = [target_path]
    else:
        files = [p for p in target_path.iterdir() if p.suffix.lower() in supported_exts]

    if not files:
        print(f"[*] No encrypted QQ Music files found in: {target_path}")
        return

    print(f"[*] QQMusic Decryptor for macOS")
    print(f"[*] Engine Architecture: {platform.machine()}")
    print(f"[*] Scanning {len(files)} file(s)...")

    udid = get_qqmusic_udid()
    configs = get_mmkv_configs(udid)
    engine = get_engine_binary()

    success_count = 0
    fail_count = 0

    for idx, f in enumerate(files, 1):
        print(f"[{idx}/{len(files)}] Decrypting: {f.name} ... ", end="", flush=True)
        ok = decrypt_file(
            engine=engine,
            file_path=f,
            output_dir=output_dir,
            mmkv_configs=configs,
            overwrite=not args.no_overwrite,
        )
        if ok:
            print("DONE")
            success_count += 1
            if args.delete_source:
                try:
                    f.unlink()
                    print(f"    (Removed source: {f.name})")
                except Exception as e:
                    print(f"    (Failed to remove source: {e})")
        else:
            print("FAILED")
            fail_count += 1

    print("\n----------------------------------------")
    print(f"Summary: {success_count} succeeded, {fail_count} failed.")
    print(f"Output directory: {output_dir}")
    print("----------------------------------------")


if __name__ == "__main__":
    main()
