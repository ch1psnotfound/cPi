# cPi 的 cFS 验证环境

源码保存在 Mac 工作区根目录下的 `cfs/`；编译和运行在 Docker 容器 `cpi-cfs-dev` 内完成。Dockerfile 按你的要求留给你编写，目前容器通过安装软件包配置，删除容器会丢失工具链，源码及构建日志仍保留在 Mac。

## 固定基线

- 官方仓库：https://github.com/nasa/cFS
- 正式版本：`v7.0.1`
- 顶层提交：`088b2fa828db9ff7e00733f1908e0eeb59f66ce3`
- 子模块：使用上述版本记录的提交，不跟随各仓库最新分支。
- Linux：Ubuntu 24.04，原生 `linux/arm64`。
- 构建配置：官方 `native_std`，调试模式、启用单元测试、关闭 EDS。
- 容器源码路径：`/workspace/cfs`。
- 当前阶段为了便于查看产物，构建目录也在 Mac 源码目录下；后续可将其单独挂载为 Docker volume。

## 本次验证结果

- `native_std` 完整编译与安装成功，未修改官方源码。
- CPU1 进入 OPERATIONAL，sample_app 初始化及短期存活检查通过。
- CPU1 官方 CTest 注册项共 198 项：188 项通过，3 项失败，7 项超时。失败与超时清单见 `cfs/build-native_std/cpi-test.log`，结构化结果见 `cfs/build-native_std/cpi-tests.xml`。本次不是测试全绿基线。
- OSAL 线程栈、消息队列及内核接口限制仍需适配；因此 `test` 和 `verify` 当前预期返回非零，不能作为生成应用独立的质量评分。后续应为生成应用增加专门测试，并区分已有基线失败。

## 重建开发容器

源码首次获取：

```bash
git clone --branch v7.0.1 --depth 1 --recurse-submodules --shallow-submodules https://github.com/nasa/cFS.git cfs
```

容器工具链配置脚本可重复执行，不生成 Dockerfile：

```bash
bash cfs-env/setup.sh
# 若需要使用本机现有代理
CFS_APT_PROXY=http://host.docker.internal:7897 bash cfs-env/setup.sh
```

Ubuntu 基础镜像已按 digest 固定；apt 软件包使用 Ubuntu 仓库当时的版本，尚不保证逐字节重建。已安装版本记录在 `cfs-env/packages.lock`。

源码保持官方版本。ARM64 上部分 OSAL 测试使用固定的小型静态线程栈，低于本环境 `PTHREAD_STACK_MIN=131072` 字节，任务创建失败后测试可能停滞。因此测试入口直接使用官方 CTest 注册项，为每个测试设置 30 秒超时，保存 JUnit 报告 `cfs/build-native_std/cpi-tests.xml`，不把环境不兼容伪装成通过。

## 日常操作

从 cPi 工作区根目录执行：

```bash
# 配置并编译，生成运行目录
bash cfs-env/cfs.sh build

# 官方测试（每项 30 秒超时，失败返回非零退出码）
bash cfs-env/cfs.sh test

# 启动、等待 OPERATIONAL 和 sample_app 初始化、检查短暂存活，然后终止
bash cfs-env/cfs.sh smoke

# 统一验证入口；任何一步失败均返回非零退出码
bash cfs-env/cfs.sh verify

# 交互运行，Ctrl+C 结束
bash cfs-env/cfs.sh run

# 容器内开发终端
bash cfs-env/cfs.sh shell

# 停止环境
bash cfs-env/cfs.sh stop
```

构建产物位于工作区根目录下的 `cfs/build-native_std/`，运行目录为 `exe/cpu1/`。启动验证输出 `cpi-smoke.log` 和 `cpi-smoke-result.json`，后者供 cPi 读取。源码修改后再次 build 即可，不需要重新创建容器。

不要并行运行多个 cFS 实例；它们会争用相同的网络端口。启动检查是短期存活验证，不等于命令、遥测或业务逻辑测试。

运行与测试使用 Ubuntu 普通用户 UID/GID 1000，避免容器 root 用户跳过 OSAL 的消息队列深度适配。当前 Linux 消息队列深度上限为 10，OSAL 开发模式会截断较大的请求；全量示例中 SBN 启动时可出现管道溢出，HS 的系统监控也因 Docker Desktop 内核没有提供 `/proc/schedstat` 而报初始化错误。核心及 sample_app 的启动检查不覆盖这些应用的健康状况。这套环境适合作为初步编译与启动基线，消息吞吐、实时性和 HS/SBN 功能验证还需单独适配配置。

## 接入 cPi 生成的应用

1. 以 `cfs/apps/sample_app` 为起点创建应用。
2. 在 `cfs/sample_defs/targets.cmake` 中加入构建目标。
3. 在 `cfs/sample_defs/generate_startup.cmake` 中加入应用加载项；此版本由它生成运行目录中的 `cf/cfe_es_startup.scr`，不要只修改生成文件。
4. 执行 `bash cfs-env/cfs.sh verify`。
5. 增加该应用自己的输入、输出断言。官方单元测试及 sample_app 启动成功不能代替生成代码的业务测试。

## 编辑器与调试

VS Code 可用 Dev Containers 的 “Attach to Running Container” 连接 `cpi-cfs-dev`，打开 `/workspace/cfs`，在容器端安装 C/C++ 扩展。工具链包含 GCC、CMake、Make、Git、GDB、Python 3。当前没有为容器开启额外调试权限；若后续需要 GDB attach，再按具体调试方式配置。

## 后续编写 Dockerfile 时使用的配置

基础镜像为 `ubuntu:24.04`，平台为 `linux/arm64`，安装以下包：

```text
build-essential cmake git gdb python3 ca-certificates pkg-config jq
```

工作目录设为 `/workspace/cfs`，将 Mac 上的 cFS 源码绑定挂载到该目录。无需 privileged 模式，也无需挂载 Docker socket。当前只验证容器内部运行；若需要从 Mac 地面站发指令，须另行映射 UDP 端口并配置遥测目标地址。

本机下载访问 GitHub 时使用了已有系统代理 `127.0.0.1:7897`。容器通过代理下载 Ubuntu 索引较慢，已切换为直连软件源。代理仅用于当次下载命令，没有修改全局 Git 或 Docker 配置。后续镜像构建时不要将本机代理地址硬编码到镜像中。
