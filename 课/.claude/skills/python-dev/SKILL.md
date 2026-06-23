---
name: python-dev
description: >
  1. 提供 Python 项目的开发、调试、依赖管理及逆向辅助。
  2. 当用户涉及 Python 字节码反编译、PyInstaller 解包、Cython 逆向、pip 包分析时调用。
  3. 核心价值：规范使用虚拟环境，安全分析 Python 打包产物和闭源模块。
version: 1.0.0
allowed_tools: [Read, Edit, Bash, Grep, Glob]
tags: [python, pip, pyinstaller, bytecode, cython]
author: reverse-agent
risk_level: LOW
---

# Python Development Skill

## 概述
本技能覆盖 Python 项目开发、虚拟环境管理、字节码反编译、PyInstaller/Cython 逆向分析。

## 前置条件
- Python >= 3.9
- 虚拟环境已创建（本项目使用 `.venv/`）
- 激活方式：
  - Bash: `source .venv/Scripts/activate`
  - CMD: `.venv\Scripts\activate.bat`
  - PowerShell: `.venv\Scripts\Activate.ps1`

## 工作流程
1. **环境管理**：
   - 激活虚拟环境
   - 安装依赖：`pip install -r requirements.txt`
   - 导出依赖：`pip freeze > requirements.txt`
2. **字节码反编译**：
   - `.pyc` 文件：`uncompyle6` 或 `decompyle3`
   - 注意 Python 版本匹配（3.9 字节码需对应工具版本）
3. **PyInstaller 解包**：
   - 使用 `pyinstxtractor.py` 提取 `PYZ-00.pyz`
   - 对提取出的 `.pyc` 进行反编译
4. **Cython 逆向**：
   - `.pyd` / `.so` 文件：先用 `strings` / `nm` 分析
   - 复杂场景使用 `Ghidra` + `retdec` 或 `decompyle++`
5. **pip 包审计**：
   - `pip show <pkg>` 查看元数据
   - 检查 `site-packages/<pkg>/` 下的可疑文件和钩子

## 最佳实践
- 始终使用虚拟环境，避免污染系统 Python。
- 分析不可信包时先在隔离环境安装并限制网络权限。
- 使用 `basedpyright` 或 `mypy` 进行静态类型检查。

## 示例
用户：帮我反编译这个 PyInstaller 打包的 exe。
→ 使用 `pyinstxtractor` 提取 → 定位主程序入口的 `.pyc` → 使用 `uncompyle6` 还原 `.py` 源码。

## 故障排查
- **uncompyle6 不支持当前版本**：尝试 `decompyle3` 或 `pycdc`。
- **PyInstaller 解包后缺少依赖**：检查 `_internal` 目录和 `PYZ` 归档完整性。
