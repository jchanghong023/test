# Spec Delta

## Purpose

提供在终端打印本机硬件与系统信息的能力，覆盖 CPU、内存、磁盘、OS、主机名与架构等字段，使用 Python 标准库实现，跨平台设计。

## ADDED Requirements

### Requirement: Print machine information to terminal

脚本运行后 MUST 在终端打印人类可读的机器信息，且 MUST NOT 保存任何文件或引入第三方依赖。

#### Scenario: Run script on supported platform

- **WHEN** 用户在 Windows 或 WSL2 CentOS 上运行脚本
- **THEN** 脚本无报错并在终端输出机器信息

### Requirement: Output required fields

输出 MUST 包含 CPU 型号及核心数、内存总量与可用量、磁盘总量与可用量、OS 名称及版本、主机名与架构。

#### Scenario: Verify all required fields present

- **WHEN** 脚本完成运行
- **THEN** 输出中可找到上述全部字段且格式清晰可读

### Requirement: Human-readable output only

输出 MUST 为人类可读文本，MUST NOT 提供 `--json` 或其他结构化输出参数。

#### Scenario: No JSON option

- **WHEN** 用户运行脚本
- **THEN** 仅输出人类可读文本，不存在 `--json` 参数

### Requirement: Platform verification boundary

在 macOS 上 MUST NOT 声明通过，除非已在 macOS 实测；Windows 与现有 WSL2 CentOS MUST 作为实测通过平台。

#### Scenario: macOS not claimed without testing

- **WHEN** 未在 macOS 实测
- **THEN** 文档与验收不得声明 macOS 通过