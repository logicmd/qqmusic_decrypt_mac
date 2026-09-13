# QQ 音乐 Mac 端离线解密工具 (QQ Music Decrypt for macOS)

[中文说明](#中文说明) | [English README](#english-readme)

---

<a name="中文说明"></a>
## 中文说明

专门为 macOS 平台 QQ 音乐客户端 (`com.tencent.QQMusicMac`) 打造的轻量级离线解密工具。能够将下载的加密音频文件（`.mflac`、`.mgg`、`.mflac0`、`.mgg1` 等）直接转换为标准无损 `.flac` 和 `.ogg` 音频格式。无需依赖 Windows 虚拟机，无需内存注入或 Hook QQ 音乐进程。

### 特性

- **原生适配 macOS**：专为 Mac 版 QQ 音乐设计，完美支持新版 `musicex` 标签和 MMKV 密钥库。
- **全自动识别**：自动从偏好设置读取客户端设备 UDID，动态推导 MMKV 数据库名与 AES/MD5 解密密钥，无需手动抓取密钥。
- **纯离线安全**：无需 Hook 正在运行的 QQ 音乐进程，无需联网，保护本地隐私。
- **双架构通用**：内置适用于 Apple Silicon (`arm64`，M1/M2/M3/M4) 与 Intel (`x86_64`) 的原生解密引擎，自动匹配。
- **批量/单曲转换**：支持一键批量解密整个下载目录，或指定单个文件转换。

### 原理解析

1. Mac 版 QQ 音乐下载的音频文件尾部带有 `musicex` 标签（192 字节），记录了歌曲 ID、Media ID 及真实文件名。
2. 音频真正的 AES 解密密钥保存在沙盒的 MMKV 键值数据库中（路径位于：`~/Library/Containers/com.tencent.QQMusicMac/Data/Library/Application Support/QQMusicMac/iData/`）。
3. 本工具自动读取 `com.tencent.QQMusicMac.plist` 中的客户端 UDID，通过凯撒移位算法与 MD5 哈希计算推导出数据库名（如 `240112`）与访问密码，提取密钥后对音频流进行离线解码还原。

### 环境要求

- macOS 10.15 及以上（支持 Apple Silicon 与 Intel 芯片）
- Python 3（macOS 系统自带）
- 电脑上已安装并登录过 QQ 音乐 Mac 客户端

### 使用方法

#### 1. 默认一键转换（批量解密所有已下载歌曲）
直接在仓库目录下运行脚本，工具将自动扫描 QQ 音乐默认下载目录并转换到当前目录的 `./output` 文件夹中：
```bash
python3 decrypt.py
```

#### 2. 解密指定文件
```bash
python3 decrypt.py -i "/path/to/song.mflac"
```

#### 3. 指定输入目录与自定义输出目录
```bash
python3 decrypt.py -i "/path/to/my_songs" -o "/path/to/flac_export"
```

#### 4. 可选参数

| 参数 | 说明 |
|---|---|
| `-i`, `--input` | 输入文件路径或目录路径（默认：QQ 音乐 Mac 客户端的 `iQmc` 文件夹） |
| `-o`, `--output` | 解密后音频保存目录（默认：`./output`） |
| `--delete-source` | 解密成功后自动删除原始加密文件 |
| `--no-overwrite` | 如果输出目录已有同名文件，则跳过不覆盖 |

---

<a name="english-readme"></a>
## English README

A dedicated, lightweight offline tool to decrypt QQ Music macOS downloaded encrypted files (`.mflac`, `.mgg`, `.mflac0`, `.mgg1`, etc.) into standard `.flac` and `.ogg` files without running Windows or injecting into QQ Music processes.

### Features

- **macOS Native:** Tailored specifically for QQ Music for Mac (`com.tencent.QQMusicMac`).
- **Auto Discovery:** Automatically resolves QQ Music client UDID, MMKV encryption keys, and default download directories.
- **Offline & Safe:** No process injection, no memory hooking, no network requests required.
- **Universal Architecture:** Bundles decryption binaries for both Apple Silicon (`arm64`) and Intel (`x86_64`) Macs.
- **Batch Processing:** Decrypt entire download folders or individual files with one command.

### How It Works

1. On macOS, QQ Music writes audio files with a `musicex` tag footer containing the track's Media ID.
2. The track's AES decryption keys are stored in an encrypted MMKV database (`~/Library/Containers/com.tencent.QQMusicMac/Data/Library/Application Support/QQMusicMac/iData/`).
3. This tool reads the client UDID from `com.tencent.QQMusicMac.plist`, derives the MMKV database name and encryption keys using the Caesar & MD5 derivation scheme, and unlocks the audio stream into lossless FLAC / OGG.

### Requirements

- macOS 10.15+ (Apple Silicon or Intel)
- Python 3 (pre-installed on macOS)
- QQ Music for Mac installed and logged in at least once

### Usage

#### 1. Default (Batch decrypt all downloads)
Simply run the script with no arguments. It will automatically scan the default QQMusicMac download directory and decrypt all files into `./output`:

```bash
python3 decrypt.py
```

#### 2. Decrypt a Specific File
```bash
python3 decrypt.py -i "/path/to/song.mflac"
```

#### 3. Decrypt a Specific Folder to a Custom Output Directory
```bash
python3 decrypt.py -i "/path/to/my_songs" -o "/path/to/flac_export"
```

#### 4. Optional Flags

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
