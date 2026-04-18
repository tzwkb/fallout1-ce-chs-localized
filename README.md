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

### 下载完整中文版游戏包

| 内容 | 下载 |
|------|------|
| 完整中文版游戏包 | [fallout1-ce-chs-gbk.zip](https://github.com/tzwkb/fallout1-ce-chs-localized/releases/download/v1.0.0/fallout1-ce-chs-gbk.zip) |

> 该压缩包为**开箱即用的完整中文版游戏包**，包含：
> - 编译好的 Fallout CE 中文版引擎（`fallout-ce.exe`）
> - 中文字体（`fonts/chs/`）
> - 已部署的 GBK 汉化文本（`DATA/TEXT/ENGLISH/`）← 对应仓库 `localization/GBK/`
> - 游戏配置文件
>
> 只需放入原版游戏的 `master.dat` 和 `critter.dat` 即可运行。

### 各平台安装步骤

#### Windows（推荐）

上方 release 中的 zip 为**开箱即用的完整中文版游戏包**（仅 Windows）。

1. 拥有原版《辐射1》（需 `master.dat` 和 `critter.dat`）
2. 下载 zip 并解压
3. 将原版 `master.dat` 和 `critter.dat` 复制到解压目录
4. 运行 `fallout-ce.exe`

> `fonts/chs/font.ini` 中 `encoding=GBK` 已默认配置。

#### macOS / Linux / Android / iOS

上方 zip **仅含 Windows 版引擎**。其他平台需：

1. 从 [yurikaka/fallout1-ce-chs/releases](https://github.com/yurikaka/fallout1-ce-chs/releases) 下载对应平台的引擎（`.app` / Linux 二进制 / `.apk` / `.ipa`）
2. 按 [原版安装指南](https://github.com/alexbatalov/fallout1-ce) 准备游戏资源（`master.dat`、`critter.dat`、`data`）
3. 获取汉化文件和字体：
   - 下载上方 zip，提取其中的 `DATA/TEXT/ENGLISH/`（汉化文件）和 `fonts/chs/`（字体）
   - 覆盖到对应平台的游戏目录
   - 或直接从仓库 `localization/GBK/` 下载文件手动部署
4. 确认 `fonts/chs/font.ini` 中 `encoding=GBK`
5. 运行游戏

**注意**：UTF-8 编码也能运行，但会导致对话框断行显示异常。**建议使用 GBK 编码版本。**

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
