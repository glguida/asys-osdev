# Installed tools

Debian 12 (bookworm) with QEMU and OpenSBI from bookworm-backports.

## Cross toolchains

Bare-metal `*-unknown-elf` toolchains in `/opt/cross-toolchain/bin` (on `PATH`),
built with https://github.com/glguida/gcc_toolchain_build. C and C++ only; no C
library. Link with `-nostdlib` and add `-lgcc` when the code needs libgcc.

| Prefix | GCC | Binutils |
| --- | --- | --- |
| `amd64-unknown-elf-` | 14.2.0 | 2.43.1 |
| `i686-unknown-elf-` | 14.2.0 | 2.43.1 |
| `riscv64-unknown-elf-` | 14.2.0 | 2.43.1 |

The host compiler is Debian's `gcc` 12 for build-time tools.

## Emulation and firmware

| Tool | Version | Notes |
| --- | --- | --- |
| `qemu-system-i386`, `qemu-system-x86_64` | 10.0.2 | `-kernel` boots multiboot ELF images |
| `qemu-system-riscv64` | 10.0.2 | `-M virt` loads OpenSBI by default; `-kernel` is placed at 0x80200000 |
| `qemu-img` and other `qemu-utils` | 10.0.2 | |
| OpenSBI | 1.5.1 | `/usr/share/qemu/opensbi-riscv64-generic-fw_dynamic.bin`, `/usr/lib/riscv64-linux-gnu/opensbi/generic/` |
| OVMF (x86_64 UEFI) | 2022.11 | `/usr/share/OVMF/OVMF_CODE_4M.fd` with `OVMF_VARS_4M.fd` (copy the vars file before use), `/usr/share/qemu/OVMF.fd` |

QEMU runs headless: use `-nographic` or `-display none` with `-serial stdio`.
A guest that idles never exits, so bound every run with `timeout`, or exit
deliberately: `-device isa-debug-exit` on x86, SBI system reset on RISC-V.

## Debugging

| Tool | Version | Use |
| --- | --- | --- |
| `gdb` | 13.1 | x86 guests |
| `gdb-multiarch` | 13.1 | RISC-V (and any other) guests |

Start QEMU with `-S -s` to wait for a debugger on port 1234, then
`gdb -ex "target remote :1234" kernel.elf`. Debug optimized code with care,
since `next` may stop before scheduled stores. Build with `-Og -g` when
stepping matters. QEMU's `-d int,cpu_reset,guest_errors -D log` traces
interrupts and faults.

## Build and source tools

`make` 4.3, `autoconf` 2.71, `automake` 1.16.5, `bison` 3.8.2, `flex` 2.6.4,
`texinfo` 6.8, `m4`, `file`, `git` 2.39.5, `python3` 3.11.2,
`device-tree-compiler` (`dtc`) 1.6.1, `mtools` 4.0.32 and `dosfstools` 4.2
for FAT/EFI system-partition images, GNU `indent` 2.2.12, `universal-ctags`,
`cscope` 15.9, `ripgrep` (`rg`) 13.0, `xxd`, `hexdump` (bsdextrautils),
`poppler-utils` (`pdftotext`, `pdfinfo`).

## Documentation

The `exokernel` skill holds the MIT Exokernel papers and theses as PDF and
searchable text in `/opt/asys/environment/skills/exokernel/papers/`.
