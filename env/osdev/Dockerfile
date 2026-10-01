# Bare-metal cross toolchains (amd64, i686, riscv64 *-unknown-elf, GCC 14.2)
# built with https://github.com/glguida/gcc_toolchain_build. Debian bookworm
# matches the asys-workers base, so the binaries run unchanged in the final image.
FROM debian:bookworm AS cross-toolchain
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential ca-certificates curl git texinfo bison flex m4 file \
      bzip2 xz-utils \
 && rm -rf /var/lib/apt/lists/*
ARG GCC_TOOLCHAIN_BUILD_REV=eecef0929616a96517a83dab988a8429ad8c62d8
RUN git clone https://github.com/glguida/gcc_toolchain_build /src/gcc_toolchain_build \
 && git -C /src/gcc_toolchain_build checkout --quiet "$GCC_TOOLCHAIN_BUILD_REV"
WORKDIR /src/gcc_toolchain_build
RUN make populate
RUN for t in amd64-unknown-elf i686-unknown-elf riscv64-unknown-elf; do \
      make MAKEOPT="-j$(nproc)" INSTALLDIR=/opt/cross-toolchain "$t-gcc" || exit 1; \
      rm -rf build; \
    done

FROM asys-workers
USER root
RUN echo "deb http://deb.debian.org/debian bookworm-backports main" \
      > /etc/apt/sources.list.d/backports.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends -t bookworm-backports \
      qemu-system-x86 qemu-system-misc qemu-utils opensbi \
      build-essential autoconf automake make file texinfo bison flex m4 \
      git ca-certificates curl bzip2 xz-utils \
      gdb gdb-multiarch ovmf device-tree-compiler mtools dosfstools \
      indent universal-ctags cscope ripgrep xxd bsdextrautils \
      poppler-utils procps \
 && rm -rf /var/lib/apt/lists/*
COPY --from=cross-toolchain /opt/cross-toolchain /opt/cross-toolchain
ENV PATH="/opt/cross-toolchain/bin:${PATH}"
COPY . /opt/asys/environment
USER node
