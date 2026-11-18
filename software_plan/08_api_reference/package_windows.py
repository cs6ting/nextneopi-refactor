#!/usr/bin/env python3
"""Package the offline API Reference site as a Windows-friendly ZIP.

The generated site is fully self-contained static HTML, so on Windows the user
can simply double-click ``index.html``. This script rebuilds the site, drops a
couple of launcher ``.bat`` files and a Chinese usage guide next to it, then
zips everything into ``dist/`` with a single top-level folder so unzipping
produces a tidy ``nextneopi-api-docs/`` directory.

Usage:
    python3 package_windows.py --pandoc /usr/local/bin/pandoc
"""

from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path

import build_html

API_ROOT = build_html.API_ROOT
OUTPUT_ROOT = build_html.OUTPUT_ROOT
DIST_ROOT = API_ROOT / "dist"
ARCHIVE_TOP = "nextneopi-api-docs"

# Batch files are ASCII-only in their commands so they run regardless of the
# console code page; all Chinese guidance lives in the .txt file.
OPEN_BAT = """@echo off
rem Open the offline nextNEOpi API Reference in the default browser.
start "" "%~dp0index.html"
"""

SERVE_BAT = """@echo off
rem Serve the docs at http://localhost:8899 for maximum fidelity.
rem Requires Python (py or python on PATH); otherwise opens the file directly.
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    start "" http://localhost:8899/index.html
    py -m http.server 8899
    goto :eof
)
where python >nul 2>nul
if %errorlevel%==0 (
    start "" http://localhost:8899/index.html
    python -m http.server 8899
    goto :eof
)
echo Python was not found on PATH. Opening the file directly instead.
start "" "%~dp0index.html"
pause
"""

# UTF-8 BOM so legacy Windows Notepad renders the Chinese correctly.
USAGE_TXT = "\ufeff" + """nextNEOpi 接口文档（离线版）使用说明
=======================================

这是一个完全离线、自包含的接口文档站点，无需安装任何软件。

【最简单：直接看】
  1. 解压本压缩包到任意目录（例如桌面）。
  2. 双击 “打开文档.bat”，或直接双击 “index.html”。
  3. 默认浏览器会打开文档首页，左侧是导航、右侧是本页目录，顶部有搜索框。

【可选：以本地服务器方式浏览（保真度最高）】
  - 双击 “启动本地服务器.bat”。
  - 如果电脑装了 Python，会在 http://localhost:8899 打开文档；
    没装 Python 会自动退回为直接打开 index.html。
  - 关闭那个黑色命令行窗口即可停止服务器。

【内容说明】
  - index.html            文档首页（Reference API）。
  - _static/              样式与脚本（离线，无需联网）。
  - _sources/             每篇文档的原始 Markdown（“查看源文档”指向这里）。
  - assets/               JSON Schema 与示例配置（可直接下载查看）。
  - design/               全部设计文档（需求/架构/模块/接口/规格/测试/质量/迁移）。
  - build-manifest.json   构建清单（页数、来源摘要、Pandoc 版本）。

【小贴士】
  - 用 Chrome / Edge / Firefox 打开体验最好。
  - 顶部搜索框可按页面标题/路径过滤左侧导航。
  - 这是“目标设计 API”，不代表功能已实现。
"""


def write_launchers() -> list[Path]:
    files = {
        OUTPUT_ROOT / "打开文档.bat": OPEN_BAT,
        OUTPUT_ROOT / "启动本地服务器.bat": SERVE_BAT,
    }
    written: list[Path] = []
    for path, text in files.items():
        # CRLF line endings for Windows batch files.
        path.write_text(text.replace("\n", "\r\n"), encoding="ascii")
        written.append(path)
    guide = OUTPUT_ROOT / "使用说明.txt"
    guide.write_text(USAGE_TXT.replace("\n", "\r\n"), encoding="utf-8")
    written.append(guide)
    return written


def make_zip() -> Path:
    DIST_ROOT.mkdir(parents=True, exist_ok=True)
    archive = DIST_ROOT / f"{ARCHIVE_TOP}-windows.zip"
    if archive.exists():
        archive.unlink()
    files = sorted(p for p in OUTPUT_ROOT.rglob("*") if p.is_file())
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            arcname = Path(ARCHIVE_TOP) / path.relative_to(OUTPUT_ROOT)
            zf.write(path, arcname.as_posix())
    return archive, len(files)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pandoc", default=shutil.which("pandoc") or "pandoc")
    parser.add_argument("--skip-build", action="store_true", help="Package the existing html/ without rebuilding")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.skip_build:
        if not shutil.which(args.pandoc) and not Path(args.pandoc).is_file():
            raise SystemExit(f"Pandoc not found: {args.pandoc}")
        build_html.build(args.pandoc)
    elif not OUTPUT_ROOT.exists():
        raise SystemExit("html/ does not exist; run without --skip-build first")

    launchers = write_launchers()
    archive, file_count = make_zip()
    size_mb = archive.stat().st_size / (1024 * 1024)
    print(f"Added {len(launchers)} launcher/guide files to {OUTPUT_ROOT}")
    print(f"Packaged {file_count} files -> {archive} ({size_mb:.2f} MiB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
