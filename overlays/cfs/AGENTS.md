# cFS — guide for AI agents

The Core Flight System (cFS) is a framework for flight software. The bundle combines the Core Flight Executive (cFE), an operating-system abstraction layer (OSAL), platform support (PSP), applications, libraries, and tools. Mission configuration selects and configures these elements for each CPU.

This file is a router. It tells you where things are; the details live in the documents linked below.

## Repository map

For NASA cFS Bundle v7.0.1. Paths are relative to the repository root. cFE, OSAL, PSP, applications, libraries, and most tools are included as Git submodules.

| Path | Contents |
| --- | --- |
| `cfe/modules/` | Core Flight Executive (cFE): application lifecycle and resource management (ES), events (EVS), software bus (SB), time (TIME), tables (TBL), cFE file formats and file utilities (FS), plus message, routing, and runtime configuration support. Public APIs are in `cfe/modules/core_api/fsw/inc/`. |
| `apps/` | Applications for file transfer, checksums, data storage, file management, housekeeping, health monitoring, limit checking, memory operations, stored commands, and bus networking. Source, configuration, and available tests are organized by application. |
| `apps/ci_lab/`, `apps/to_lab/`, `apps/sch_lab/` | Lab applications: ingest UDP uplink messages into the software bus, forward subscribed messages over UDP, and send periodic messages according to a schedule table, respectively. |
| `apps/sample_app/` | Reference application demonstrating initialization, message reception and command dispatch, telemetry, tables, and unit tests. Start here when developing an application. |
| `libs/` | Libraries shared by applications. `sample_lib` demonstrates library initialization, public interfaces, application dependencies, and test stubs. |
| `osal/` | Operating System Abstraction Layer: task, synchronization, queue, time, filesystem, module-loading, and network APIs, with shared code, OS-specific implementations, BSP startup support, and test facilities. |
| `psp/` | Platform Support Package: cFE platform startup, reset, reserved memory, memory access, and exception handling, with platform implementations and modules for timebases, I/O, simulated EEPROM, and system monitoring selected by the PSP and mission configuration. |
| `sample_defs/` | Example mission configuration used by `native_std` and `native_eds`: CPUs and application lists, configuration overrides, message IDs, tables, toolchains, and installation rules. `generate_startup.cmake` generates the startup loading script. |
| `simple_defs/` | Symlink to the basic mission configuration example supplied with cFE, including a static startup script. Select it with `MISSIONCONFIG=simple`. |
| `Makefile`, `target-configs.mk`, `target-rules.mk`, `cfe/cmake/` | Build entry points and CMake infrastructure for multiple configurations: mission and architecture builds, configuration-header generation, application and library registration, table builds, installation, and testing. |
| `tools/` | Ground system and command/telemetry tools, COSMOS integration, table-file conversion and CRC tools, and the optional EDS toolchain and runtime libraries. |
| `cfe/docs/`, `osal/docs/`, `psp/docs/` | cFE user and application-development documentation, OSAL and PSP documentation, and documentation-generation inputs. |
| `actions/`, `.github/` | Reusable GitHub Actions, CI workflows for builds, tests, and static analysis, and repository collaboration configuration. |
| `build-native_std/` | Output directory for `native_std`: generated configuration headers and binaries, CPU runtime trees staged by `native_std.install` under `exe/cpu1/` and `exe/cpu2/`, host tools under `exe/host/`, and test output when tests are run. Do not edit generated files. |

For a narrative tour of the tree, see
[`docs/user-manual/overview/source-tree.md`](docs/user-manual/overview/source-tree.md).

## Anatomy of a cFS Application

The application is the unit of flight-software functionality managed by cFE
Executive Services (ES). It owns a main task, application state, and resources
such as Software Bus (SB) pipes and table handles; it may also create child
tasks. Prefer published SB messages for asynchronous communication between
applications. Use shared libraries to reuse common functions and data-processing
logic; keep library APIs distinct from SB message interfaces. Do not introduce
shared global variables merely to exchange data between applications. A
software-only application uses cFE and OSAL services to remain portable; a
hardware-servicing application also needs a deliberate boundary between device
access and application processing.

Use `apps/sample_app/` as a concrete example of the relationships below. File
names and task/pipe arrangements vary across applications.

- **Lifecycle and resource ownership.** ES registers an application before
  invoking its entry point. In `fsw/src/sample_app.c`, `SAMPLE_APP_Main` calls
  initialization, runs under `CFE_ES_RunLoop`, waits for messages with
  `CFE_SB_ReceiveBuffer`, dispatches successful receives, and exits through
  `CFE_ES_ExitApp`. Initialization registers with EVS, initializes telemetry,
  creates a pipe and subscriptions, and registers/loads the example table.
  `sample_app.h` defines the private state holding run status, counters,
  telemetry, the pipe ID, and table handles. Consolidate resource allocation
  during initialization, handle initialization/receive failures, and arrange
  safe shutdown of any child tasks.
- **Message-driven execution and commands.** SB routes a transmitted message
  to pipes subscribed to its Message ID; the receiving task processes queued
  messages. A subscription defines what the application receives, while a
  scheduler or another producer determines when messages arrive. In
  `fsw/src/sample_app_dispatch.c`, `SAMPLE_APP_TaskPipe` distinguishes the
  housekeeping-request MID from the ground-command MID. Ground commands are
  further selected by function code and checked for the expected length before
  invoking handlers in `sample_app_cmds.c`. Keep message identification,
  validation, and dispatch consistent with handler argument types. Use cFE
  message APIs to access headers and treat Message IDs as opaque. Treat the
  received SB buffer as a transient receive resource. Copy any data that must
  outlive the current receive operation into application-owned storage before
  releasing or reusing the buffer. With `CFE_SB_ReceiveBuffer`, do this before
  the next receive on the same pipe, which releases the previous buffer.
- **Telemetry and operational events.** The application owns the content and
  production of its telemetry. In `sample_app`, a housekeeping request invokes
  `SAMPLE_APP_SendHkCmd`, which copies counters into the telemetry payload,
  timestamps the packet, and transmits it on SB. Mission scheduling must supply
  that request to obtain periodic reports. EVS events report occurrences such
  as startup, command execution, and errors, using IDs declared in
  `fsw/inc/sample_app_eventids.h`. Keep telemetry, command counters, and event
  reporting consistent with actual processing outcomes.
- **Runtime tables.** Table Services (TBL) manages loadable application data
  that can be validated and activated during operation. The application
  registers its table and validation callback, loads initial data, services
  pending updates, and acquires/releases addresses when using active data.
  `sample_app.c`, `sample_app_cmds.c`, and `sample_app_utils.c` share these
  responsibilities; the sample calls `CFE_TBL_Manage` on housekeeping requests.
  Follow the actual application's division of responsibilities; do not create
  `*_utils.c` or `*_cmds.c` solely to reproduce the sample's file layout.
  `fsw/tables/sample_app_tbl.c` supplies initial values and `CFE_TBL_FILEDEF`
  metadata for a loadable `.tbl` image. Keep the table definition, image, and
  validation logic consistent, and release acquired addresses so updates can
  proceed. Use SB for inter-application communication.
- **Interface definitions and build-time configuration.** Public/interface
  headers live in `fsw/inc/`; implementation and private headers live in
  `fsw/src/`. In `config/`, message payload definitions (`*_msgdefs.h`) are
  separated from packet structures (`*_msgstruct.h`), which add the message
  headers. Table definitions follow the `*_tbldefs.h` / `*_tblstruct.h` split;
  `*_msg.h` and `*_tbl.h` combine the relevant definitions. Function codes,
  Message IDs, performance IDs, and mission/platform settings connect these
  interfaces to the deployment. Distribution defaults use a `default_` prefix;
  the selected mission `_defs` directory can override them with unprefixed
  headers. `mission_build.cmake` and `arch_build.cmake` register configuration
  headers for generated include wrappers. With `CFE_EDS_ENABLED`,
  `eds/sample_app.xml` supplies definitions used to generate interface and
  dispatch support; `config/eds_*.h` adapters and `sample_app_eds_dispatch.c`
  connect that support to the application. **Edit the source selected by the
  build: default headers, mission overrides, or EDS for generated definitions.**
  Do not infer the active interface source from filenames alone. Inspect the
  selected mission, build configuration, and EDS settings to determine which
  definitions are authoritative. Propagate interface changes to consuming
  applications, ground tools, and tests.
- **Build, mission integration, and verification.** The application
  `CMakeLists.txt` registers sources with `add_cfe_app`, library dependencies,
  table builds, and optional `unit-test/` coverage tests using UT Assert and
  stubs. The mission selects which applications/libraries are built for each
  CPU and how they are started. In this bundle, `sample_defs/targets.cmake`
  selects them and `sample_defs/generate_startup.cmake` generates startup entries
  specifying module, entry point, application name, priority, and stack size.
  Keep library load order, installed table paths, Message ID assignments,
  scheduler messages, and telemetry subscriptions consistent with application
  initialization. Verify both application behavior and its mission connections;
  registering a build target alone does not start or schedule the application.

Keep application design documentation in sync where provided. Generated
configuration wrappers, EDS support, binaries, and table images under the
selected build directory (e.g. `build-native_std/`) are build products. Never
edit them; update their source inputs and rebuild.
