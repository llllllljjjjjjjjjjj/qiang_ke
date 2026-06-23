---
name: reverse-engineering
description: >
  1. 提供二进制分析、反汇编、反编译和动态调试指导。
  2. 当用户涉及 PE/ELF 文件分析、汇编代码、逆向逻辑还原、Hook 技术、加解密算法还原时调用。
  3. 核心价值：安全地分析未知二进制行为并输出结构化逆向报告，避免触发杀软或损坏原始样本。
version: 1.0.0
allowed_tools: [Read, Edit, Bash, Grep]
tags: [reverse, binary, disassembly, security, malware-analysis]
author: reverse-agent
risk_level: HIGH
---

# Reverse Engineering Skill

## 概述
本技能用于辅助对二进制文件、混淆脚本、加密逻辑进行安全逆向分析。强调**只读优先、隔离环境、行为记录**。

## 前置条件
- 分析工作应在隔离环境（虚拟机 / Docker / 沙盒）中进行。
- 原始样本必须先备份，所有操作针对副本。
- 敏感样本（疑似恶意软件）禁止直接上传到公共平台。

## 工作流程
1. **信息收集**：使用 `file`, `strings`, `ldd`, `pefile` 等工具提取元数据。
2. **静态分析**：
   - 推荐工具：IDA Pro / Ghidra / Binary Ninja / radare2 / Cutter
   - 关注入口点、导入表、字符串表、资源节
3. **动态分析**（如需要）：
   - 推荐工具：x64dbg / OllyDbg / Frida / DynamoRIO
   - 必须先在快照环境中运行
4. **逻辑还原**：将汇编/字节码还原为伪代码或流程图。
5. **输出报告**：按以下结构输出发现：
   - 样本基本信息（哈希、编译器、加壳信息）
   - 关键函数列表
   - 算法/协议还原（如有）
   - IoC（失陷指标，仅限恶意软件分析）

## 最佳实践
- 优先静态分析，尽量减少动态执行。
- 遇到加壳样本先尝试自动脱壳（upx -d, unpacme 等）。
- 对可疑字符串和 API 调用保持敏感（VirtualProtect, WriteProcessMemory, InternetOpen 等）。

## 示例
用户：帮我分析这个 ELF 文件的行为。
→ 使用 `file` 和 `strings` 初筛 → 在隔离环境用 `radare2` 分析主逻辑 → 输出函数调用图和可疑行为摘要。

## 故障排查
- **无法识别编译器**：尝试 `Detect It Easy (DIE)` 或 `Exeinfo PE`。
- **anti-debug 触发**：使用 ScyllaHide、TitanHide 或基于虚拟化的调试方案。
