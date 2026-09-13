# QQ Music Decrypt for macOS (QQ音乐 Mac 端解密工具)

A dedicated, lightweight offline tool to decrypt QQ Music macOS downloaded encrypted files (`.mflac`, `.mgg`, `.mflac0`, `.mgg1`, etc.) into standard `.flac` and `.ogg` files without running Windows or injecting into QQ Music processes.

---

## Features

- **macOS Native:** Tailored specifically for QQ Music for Mac (`com.tencent.QQMusicMac`).
- **Auto Discovery:** Automatically resolves QQ Music client UDID, MMKV encryption keys, and default download directories.
- **Offline & Safe:** No process injection, no memory hooking, no network requests required.
- **Universal Architecture:** Bundles decryption binaries for both Apple Silicon (`arm64`) and Intel (`x86_64`) Macs.
- **Batch Processing:** Decrypt entire download folders or individual files with one command.

---

## How It Works

1. On macOS, QQ Music writes audio files with a `musicex` tag footer containing the track's Media ID.
2. The track's AES decryption keys are stored in an encrypted MMKV database (`~/Library/Containers/com.tencent.QQMusicMac/Data/Library/Application Support/QQMusicMac/iData/`).
3. This tool reads the client UDID from `com.tencent.QQMusicMac.plist`, derives the MMKV database name and encryption keys using the Caesar & MD5 derivation scheme, and unlocks the audio stream into lossless FLAC / OGG.

---

## Requirements

- macOS 10.15+ (Apple Silicon or Intel)
- Python 3 (pre-installed on macOS)
- QQ Music for Mac installed and logged in at least once

---

## Usage

### 1. Default (Batch decrypt all downloads)
Simply run the script with no arguments. It will automatically scan the default QQMusicMac download directory and decrypt all files into `./output`:

```bash
python3 decrypt.py
```

### 2. Decrypt a Specific File
```bash
python3 decrypt.py -i "/path/to/song.mflac"
```

### 3. Decrypt a Specific Folder to a Custom Output Directory
```bash
python3 decrypt.py -i "/path/to/my_songs" -o "/path/to/flac_export"
```

### 4. Optional Flags

| Flag | Description |
|---|---|
| `-i`, `--input` | Path to an input file or directory (default: QQ Music Mac's `iQmc` folder) |
| `-o`, `--output` | Destination directory for decrypted files (default: `./output`) |
| `--delete-source` | Automatically delete original encrypted file after successful decryption |
| `--no-overwrite` | Do not overwrite files if they already exist in the output directory |

---

## License & Credits

- Decryption core powered by [Unlock Music](https://github.com/unlock-music/unlock-music) engine.
- Distributed for personal learning and interoperability purposes under MIT License.
