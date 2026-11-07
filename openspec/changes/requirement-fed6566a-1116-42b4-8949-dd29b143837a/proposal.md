# Proposal

## Why

仓库目前没有机器信息采集脚本，开发/运维人员在本机或服务器上需要快速确认硬件与系统环境，却缺乏轻量、无外部依赖的工具。本需求新增一个 Python 脚本，运行后直接在终端打印机器信息，覆盖 Windows 与现有 WSL2 CentOS 实测平台，macOS 仅作为可移植性设计目标。

## What Changes

- 新增 Python 脚本，运行后在终端打印机器信息（仅终端输出，不保存文件）。
- 输出字段：CPU 型号及核心数、内存总量与可用量、磁盘总量与可用量、OS 名称及版本、主机名、架构。
- 输出格式为人类可读文本，不支持 `--json` 等可选参数。
- 仅使用 Python 标准库及操作系统原生命令，不引入第三方依赖。
- 不修改现有仓库文件，仅新增脚本。

## Capabilities

### New Capabilities

- `machine-info`: 提供在终端打印本机硬件与系统信息的能力，覆盖 CPU、内存、磁盘、OS、主机名与架构等字段，使用标准库实现，跨平台设计。

### Modified Capabilities

无。

## Impact

- 新增单个 Python 脚本文件；不修改现有文件、API、依赖或系统。
- 验收边界：Windows 与现有 WSL2 CentOS 实测通过；macOS 仅作为可移植性设计目标，未实测前不得声明通过。