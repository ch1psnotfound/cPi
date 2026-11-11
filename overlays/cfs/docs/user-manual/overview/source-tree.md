# A Tour of the Source Tree

The cFS Bundle contains framework code, applications, libraries, tools, and example mission configurations. This tour describes the directories in NASA cFS Bundle v7.0.1. Paths are relative to the bundle root. cFE, OSAL, PSP, applications, libraries, and most tools are included as Git submodules.

Configuration headers, executables, shared modules, and binary table files produced by the build are considered build products. Their source directories and purpose are described below.

## cfe

The [cfe](../../../cfe/) directory contains the Core Flight Executive. It provides the common services used by applications, including application management, events, message delivery, time, and tables. The services and supporting interfaces are organized under the modules directory.

### modules/core_api

This directory contains the public interfaces and common types used by applications and core services. Its fsw/inc directory includes cfe.h and the service API headers. The core_api CMake target collects the public include directories and configuration of the core modules.

### modules/core_private

This directory contains interfaces and shared definitions used internally by the core services. These definitions support cooperation between core modules.

### modules/es

Executive Services manages application startup and lifecycle, application resources, performance logging, and reset coordination. It processes the startup script that identifies libraries and applications to load, their entry points, and their execution settings.

### modules/evs

Event Services provides event registration, filtering, reporting, and logging. Applications use this service to report initialization, command processing, and error conditions. Events can be made available to other applications through the software bus.

### modules/sb

The Software Bus delivers messages to subscribed pipes. Applications create pipes, subscribe to message identifiers, transmit messages, and receive messages from those pipes. The implementation uses OSAL queues to support delivery.

### modules/time

Time Services maintains spacecraft time and supports synchronization and time-related messages. Applications use its interfaces for time values, while other framework mechanisms use its timing services.

### modules/tbl

Table Services manages application tables. It provides registration, file loading, validation, access, and update mechanisms. Applications supply table definitions and may provide validation functions for incoming table data.

### modules/fs

File Services provides cFE file-header operations, filename helpers, and file-related utilities. The underlying file, directory, and filesystem operations are supplied by OSAL.

### modules/msg

This directory contains the standard message-header implementation. It provides access to fields such as message identifiers, sizes, function codes, and timestamps. EDS builds select an alternative implementation from the EDS integration modules.

### modules/sbr, modules/resourceid, modules/config

These directories contain software-bus routing support, resource-identifier support, and the runtime configuration service. They provide mechanisms used by the core services and their public interfaces.

### modules/cfe_assert, modules/cfe_testcase

These directories contain functional-test support. The assertion library records test results, and the testcase application provides framework test cases. Their inclusion in a build and their loading into a running system are controlled separately.

### cmake

This directory contains the mission and architecture build infrastructure. It discovers modules, selects configuration files, registers applications and libraries, builds tables, and creates installation rules. The cfe top-level CMakeLists.txt selects the mission-level or architecture-level build functions.

### docs

This directory contains cFE user documentation, requirements, naming conventions, functional-test documentation, and documentation-generation inputs. The [Application Developers Guide](../../../cfe/docs/cFE%20Application%20Developers%20Guide.md) describes application development using cFE.

## apps

The [apps](../../../apps/) directory contains applications that use the framework services. Each application organizes its implementation and configuration within its own directory. The application lists in the mission configuration determine which applications are built for each CPU.

### sample_app

This directory contains a reference application with initialization, a software-bus receive loop, command dispatch, telemetry, and table handling. Its fsw/src directory contains the implementation, fsw/inc contains application headers, config contains default interface and configuration definitions, and fsw/tables contains default table data. The unit-test directory contains tests and test support.

The application initializes its resources, subscribes to command and housekeeping-request messages, and processes received messages in its main loop. Its CMakeLists.txt registers sources, tables, tests, and a dependency on sample_lib.

### ci_lab

Command Ingest Lab receives uplink data through a UDP socket. It decodes the received data into messages and transmits those messages onto the software bus.

### to_lab

Telemetry Output Lab receives subscribed software-bus messages and forwards them through a UDP socket. Its subscription table selects the messages to collect. Output is enabled by command.

### sch_lab

Scheduler Lab sends periodic software-bus messages according to a schedule table. Those messages can request housekeeping or trigger application processing. The application controls message publication rather than operating-system thread scheduling.

### cf

This directory contains the CFDP file-transfer application. It provides file-transfer processing and associated configuration and tables.

### cs

This directory contains the Checksum application. It computes and compares checksums for configured memory regions, application and library code segments, and tables, with cFE and OS code-segment checks where supported by the platform.

### ds

This directory contains the Data Storage application. It selects software-bus messages using filtering configuration and writes data to destination files.

### fm

This directory contains the File Manager application. It provides commanded file and directory operations, file information, and storage-space monitoring.

### hk

This directory contains the Housekeeping application. It assembles output housekeeping packets by copying configured fields from incoming messages.

### hs

This directory contains the Health and Safety application. It monitors application execution and selected events, performs configured response actions, services the platform watchdog, and reports CPU utilization when supported by the platform.

### lc

This directory contains the Limit Checker application. It evaluates watchpoints against received data and combines their results into actionpoints. An active actionpoint can request a configured relative-time command sequence when its failure threshold is reached.

### md

This directory contains the Memory Dwell application. It samples configured memory locations and reports the sampled data in telemetry.

### mm

This directory contains the Memory Manager application. It provides commanded memory operations, including loading, dumping, and inspecting memory through supported platform interfaces.

### sc

This directory contains the Stored Command application. It executes stored command sequences using absolute-time and relative-time sequencing mechanisms.

### sbn

This directory contains Software Bus Networking. It exchanges messages and subscription information between processors through protocol modules. The sbn_udp and sbn_f_remap entries under apps are symlinks to the UDP protocol and remapping-filter modules within this directory.

## libs

The [libs](../../../libs/) directory contains libraries used by applications. Libraries can expose callable interfaces and initialization functions without having an application's message-processing loop.

### sample_lib

This directory contains a reference library. Its fsw/public_inc directory exports its public interface, while fsw/src contains its implementation and initialization function. The library also provides unit tests and stubs. The example startup script loads it using a CFE_LIB entry.

## osal

The [osal](../../../osal/) directory contains the Operating System Abstraction Layer. It provides common interfaces for tasks, queues, synchronization, timers, files, module loading, and networking, allowing framework and application code to use these facilities across supported operating systems.

### src/os/inc

This directory contains public API headers and types. The headers describe the operations available to code using OSAL.

### src/os/shared

This directory contains common API logic and resource handling. It performs shared processing before invoking the operating-system implementation.

### src/os/posix, src/os/rtems, src/os/vxworks

These directories contain POSIX, RTEMS, and VxWorks implementations. They translate OSAL operations into facilities such as threads, message queues, semaphores, and sockets. Additional implementations include qnx and vxworks-rtp, which reuse POSIX code; src/os/portable contains implementations shared across OS targets.

### src/bsp

This directory contains board-support startup and execution code. On the generic Linux path, BSP startup initializes its support and calls OS_Application_Startup, supplied by PSP for the cFE executable.

### src/tests, src/unit-tests, src/unit-test-coverage

These directories contain API tests and coverage tests. Test stubs are provided under src/ut-stubs, and the ut_assert directory provides assertion and test-support facilities.

## psp

The [psp](../../../psp/) directory contains the Platform Support Package. It supplies cFE startup, reset, reserved-memory handling, memory access, exception handling, and other platform operations.

### fsw/inc

This directory contains public PSP interfaces. These interfaces define the platform operations used by cFE and applications that require platform access.

### fsw/pc-linux, fsw/pc-rtems

These directories contain platform implementations for Linux and RTEMS targets. Other platform implementations are also organized beneath fsw. Platform code cooperates with OSAL startup support and the common PSP implementation.

### fsw/shared

This directory contains PSP code shared by platform implementations, including common initialization and platform-support logic.

### fsw/modules

This directory contains platform modules for timebases, I/O, memory access, EEPROM, and system monitoring, selected by the PSP and mission configuration. Some modules provide simulated operations or report an operation as unimplemented when a platform does not supply that capability.

### unit-test-coverage, ut-stubs

These directories contain PSP coverage tests and stub implementations used by tests.

## sample_defs

The [sample_defs](../../../sample_defs/) directory contains the example mission configuration selected by native_std and native_eds. It defines how CPUs, applications, libraries, platform configuration, and table data are assembled into a mission build.

The targets.cmake file defines the CPUs and their application lists. The generate_startup.cmake file generates the loading script with application and library entry points, names, priorities, and stack sizes. The two files control different aspects of the system: the build includes the selected modules, and the startup script identifies the dynamically loaded modules to initialize.

### cpu1, cpu2

These directories contain CPU-specific configuration and installation customization. Their install_custom.cmake files integrate tables and invoke startup-script generation for the corresponding CPU.

### tables

This directory contains mission table data, including the Scheduler Lab schedule, Telemetry Output Lab subscriptions, and alternative application tables. The table build produces binary table files for installation into the CPU runtime trees.

### Configuration and toolchain files

The remaining configuration files provide mission and platform overrides, OSAL and PSP settings, build options, and toolchain definitions. The build selects these inputs together with the defaults provided by individual modules. It generates include wrappers for the effective configuration headers.

## simple_defs

The [simple_defs](../../../simple_defs/) entry is a symlink to cfe/cmake/sample_defs. It provides a smaller mission configuration example with a static CPU1 startup script. MISSIONCONFIG=simple selects this configuration. The simple.mk entry is a separate symlink to cFE's sample Makefile.

## tools

The [tools](../../../tools/) directory contains host tools, ground-system integrations, and optional EDS support.

### cFS-GroundSystem, cfs-cosmos-plugin

These directories contain the cFS ground system and COSMOS integration. They support interaction with the running flight software through commanding and telemetry.

### commandline-tools

This directory contains the cmd_send and tlm_recv utilities. They provide command transmission and telemetry reception, with optional EDS encoding and decoding support.

### elf2cfetbl, tblCRCTool

These directories contain table-processing utilities. elf2cfetbl extracts table data and metadata from an ELF object file to produce a cFE table image. tblCRCTool calculates a table file's CRC.

### eds

This directory contains the Electronic Data Sheets toolchain, runtime libraries, and cFE integration. Applications and framework modules provide EDS descriptions in their own eds directories. The native_eds configuration enables this support, while native_std uses the non-EDS configuration.

## actions and .github

The [actions](../../../actions/) directory contains reusable GitHub Actions for application setup, builds, analysis, and container execution. The [.github](../../../.github/) directory contains CI workflows and repository collaboration configuration.

## Build files and output directories

The root Makefile provides configuration-specific build goals. The target-configs.mk file defines configurations and preparation options, and target-rules.mk invokes configuration, compilation, installation, and test processing through the CMake infrastructure.

The native_std configuration uses build-native_std as its output directory. The native_std.install goal stages CPU executables, application modules, tables, and startup scripts under exe/cpu1 and exe/cpu2, and host utilities under exe/host. Configuration headers and intermediate files are generated during the build; test output is produced when tests are run.
