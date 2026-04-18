# Fallout 1 中文本地化 / Fallout 1 Chinese Localization

> 本仓库是《辐射1》的完整中文汉化补丁，基于 [yurikaka/fallout1-ce-chs](https://github.com/yurikaka/fallout1-ce-chs) 的中文渲染引擎。

---

## 仓库结构

```
localization/
  ├── GBK/              ← GBK 编码汉化文件（✅ 推荐使用）
  │   ├── CUTS/         ← 过场字幕
  │   ├── DIALOG/       ← NPC 对话
  │   ├── GAME/         ← 系统消息
  │   ├── CREDITS.TXT
  │   └── QUOTES.TXT
  └── UTF-8/            ← UTF-8 编码汉化文件（⚠️ 存在断行显示问题）
      ├── CUTS/
      ├── DIALOG/
      ├── GAME/
      ├── CREDITS.TXT
      └── QUOTES.TXT

localization_tools/     ← 翻译工具
  ├── translator.py     ← AI 批量翻译脚本
  └── converter.py      ← UTF-8 转 GBK 编码转换
```

---

## 安装与使用（中文版）

### 下载编译好的中文版引擎

| 平台 | 下载 |
|------|------|
| Windows x64 | [fallout-ce-windows-x64.zip](https://github.com/yurikaka/fallout1-ce-chs/releases) |
| Windows x86 | [fallout-ce-windows-x86.zip](https://github.com/yurikaka/fallout1-ce-chs/releases) |
| Android | [fallout-ce-android.apk](https://github.com/yurikaka/fallout1-ce-chs/releases) |
| iOS | [fallout-ce-ios.ipa](https://github.com/yurikaka/fallout1-ce-chs/releases) |
| Linux | [fallout-ce-linux-x64.tar.gz](https://github.com/yurikaka/fallout1-ce-chs/releases) |

Release 页面：[yurikaka/fallout1-ce-chs/releases](https://github.com/yurikaka/fallout1-ce-chs/releases)

### 下载汉化补丁

| 内容 | 下载 |
|------|------|
| 汉化补丁 GBK 版（推荐） | [fallout1-ce-chs-gbk.zip](https://github.com/tzwkb/fallout1-ce-chs-localized/releases/download/v1.0.0/fallout1-ce-chs-gbk.zip) |

> 直接下载上方压缩包即可，无需从仓库逐个下载文件。

### 各平台安装步骤

> 以下在 [Fallout Community Edition](https://github.com/alexbatalov/fallout1-ce) 原版安装指南的基础上，补充了中文版特有的字体与汉化文件配置。

#### Windows

1. 下载 `fallout-ce-windows-x64.zip`（或 x86），解压得到 `fallout-ce.exe` 和 `fonts/` 文件夹。
2. 将上述文件复制到你的 `Fallout` 游戏目录（与 `falloutw.exe` 同级）。
3. 下载汉化补丁压缩包，将其中 `localization/GBK/` 内的全部文件覆盖到游戏目录的 `data/text/english/` 下。
4. 确认 `fonts/chs/font.ini` 中 `encoding=GBK`。
5. 运行 `fallout-ce.exe`。

**注意**：UTF-8 编码也能运行，但会导致对话框断行显示异常。**建议使用 GBK 编码版本。**

#### Linux

- 以 Windows 版游戏资源为基础（包含 `master.dat`、`critter.dat` 和 `data` 文件夹）。将 `Fallout` 文件夹复制到合适位置，例如 `/home/john/Desktop/Fallout`。
- 或者从 GoG 安装包提取所需文件：

```console
$ sudo apt install innoextract
$ innoextract ~/Downloads/setup_fallout_2.1.0.18.exe -I app
$ mv app Fallout
```

- 下载并复制 `fallout-ce` 到该文件夹。
- 下载汉化补丁压缩包，将其中 `localization/GBK/` 覆盖到 `Fallout/data/text/english/`。
- 确认 `fonts/chs/font.ini` 中 `encoding=GBK`。
- 安装 [SDL2](https://libsdl.org/download-2.0.php)：

```console
$ sudo apt install libsdl2-2.0-0
```

- 运行 `./fallout-ce`。

#### macOS

> **注意**：需要 macOS 10.11 (El Capitan) 或更高版本。原生支持 Intel Mac 和 Apple Silicon。

- 以 Windows 版游戏资源为基础。将 `Fallout` 文件夹复制到合适位置，例如 `/Applications/Fallout`。
- 或者从 MacPlay/The Omni Group 版本提取资源：挂载 CD/DMG，右键 `Fallout` -> 显示包内容，进入 `Contents/Resources`，复制 `GameData` 文件夹到 `/Applications/Fallout`。
- 或者通过 Homebrew + innoextract 从 GoG 安装包提取：

```console
$ brew install innoextract
$ innoextract ~/Downloads/setup_fallout_2.1.0.18.exe -I app
$ mv app /Applications/Fallout
```

- 下载并复制 `fallout-ce.app` 到该文件夹。
- 下载汉化补丁压缩包，将其中 `localization/GBK/` 覆盖到 `Fallout/data/text/english/`。
- 确认 `fonts/chs/font.ini` 中 `encoding=GBK`。
- 运行 `fallout-ce.app`。

#### Android

> **注意**：Fallout 是为鼠标操作设计的游戏，部分操作需要精确的指针定位，触屏体验不如鼠标。当前控制方案类似触控板：
> - 单指滑动移动鼠标指针
> - 单指点击 = 左键
> - 双指点击 = 右键（切换指针模式）
> - 双指滑动 = 滚动当前视图（地图、世界地图、物品栏等）

> **注意**：从 Android 系统角度，Release 版和 Debug 版被视为不同应用，各自需要独立的游戏资源和存档。普通玩家只需使用 Release 版即可。

- 以 Windows 版游戏资源为基础。将 `Fallout` 文件夹复制到设备，例如 `Downloads`。你需要 `master.dat`、`critter.dat` 和 `data` 文件夹。注意文件名需保持小写（参见下方的 [Configuration](#configuration)）。
- 下载 `fallout-ce.apk` 并复制到设备，用文件管理器打开安装（需允许未知来源安装）。
- 首次运行游戏时会弹出文件选择器，选择第一步中的文件夹。等待数据复制完成（约 30 秒），游戏将自动启动。
- 安装完成后，将本仓库 `localization/GBK/` 通过文件管理器覆盖到设备的游戏数据目录 `data/text/english/` 下。
- 确认 `fonts/chs/font.ini` 中 `encoding=GBK`。

#### iOS

> **注意**：触控方式参见 Android 说明。

- 下载 `fallout-ce.ipa`，使用侧载工具（[AltStore](https://altstore.io/) 或 [Sideloadly](https://sideloadly.io/)）安装到设备。也可以自行从源码构建并签名。
- 首次运行游戏会看到 "Could not find the master datafile..." 的错误提示，这一步是为了让 iOS 通过文件共享暴露该应用。
- 使用 Finder（macOS Catalina 及更新版本）或 iTunes（Windows 和 macOS Mojave 及更早版本）将 `master.dat`、`critter.dat` 和 `data` 文件夹复制到 "Fallout" 应用中（[操作指南](https://support.apple.com/HT210598)）。注意文件名保持小写（参见下方的 [Configuration](#configuration)）。
- 通过文件共享将本仓库 `localization/GBK/` 复制到应用的 `data/text/english/` 目录下。
- 确认 `fonts/chs/font.ini` 中 `encoding=GBK`。

---

## Configuration

主配置文件为 `fallout.cfg`。根据你的游戏发行版本，`master.dat`、`critter.dat` 和 `data` 文件夹的文件名可能是全小写或全大写。你可以修改 `master_dat`、`critter_dat`、`master_patches` 和 `critter_patches` 设置以匹配你的文件名，或者将文件重命名为与 `fallout.cfg` 中的条目一致。

`sound` 文件夹（内含 `music` 文件夹）可能位于 `data` 文件夹内，也可能直接在 Fallout 根目录下。修改 `music_path1` 以匹配你的目录结构，通常为 `data/sound/music/` 或 `sound/music/`。音乐文件本身（`ACM` 扩展名）应保持大写，不受 `sound` 和 `music` 文件夹大小写影响。

第二个配置文件是 `f1_res.ini`，用于修改游戏窗口大小和全屏模式：

```ini
[MAIN]
SCR_WIDTH=1280
SCR_HEIGHT=720
WINDOWED=1
```

推荐设置：
- **桌面端**：使用任意你觉得合适的分辨率。
- **平板**：设置为设备的逻辑分辨率，例如 iPad Pro 11 的像素分辨率为 1668x2388，但逻辑分辨率为 834x1194。
- **手机**：将高度设为 480，根据屏幕宽高比计算宽度，例如三星 S21 为 20:9，宽度应为 480 * 20 / 9 = 1067。

目前这些设置需要手动修改，未来会提供游戏内界面配置。

---

## Contributing

当前目标：

- **更新到 v1.2**：本项目基于 1997 年 11 月发布的 Reference Edition（v1.1）。1998 年 3 月发布的 v1.2 至少包含了重要的多语言支持。
- **反向移植 Fallout 2 功能**：Fallout 2（含部分 Sfall 扩展）为原版引擎添加了许多优秀的改进和生活质量增强，其中很多值得反向移植到 Fallout 1。请记住这是另一款游戏，玩法平衡略有不同（而平衡本身就是一件很微妙的事）。

如果你有建议或功能请求，请提交 Issue。

---

## 技术栈

- **翻译**：AI 辅助（`translator.py`）
- **编码转换**：iconv + `converter.py`（UTF-8 → GBK）
- **引擎**：Fallout CE（C++17，中文字体渲染修复）
- **字体渲染**：FreeType 2.0

---

## License

引擎源码遵循 [Sustainable Use License](LICENSE.md)。

- **游戏**：© Interplay Productions / Bethesda Softworks
- **翻译**：原创作品，仅供教育用途
- **要求**：拥有原版游戏
