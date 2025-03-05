# Cross-Compiling QPDFTools from Linux to Windows

This guide explains how to set up a cross-compilation environment on Linux to build Windows executables.

## Prerequisites

Install the required packages:

```bash
# For Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y build-essential cmake git python3 python3-pip
```

## Method 1: Using MXE (M cross environment)

MXE is a powerful tool that provides a complete cross-compilation environment for building Windows applications on Linux.

### 1. Install MXE and its dependencies

```bash
# Install MXE dependencies
sudo apt-get install -y \
    autoconf automake autopoint bash bison bzip2 flex g++ \
    g++-multilib gettext git gperf intltool libc6-dev-i386 \
    libgdk-pixbuf2.0-dev libltdl-dev libssl-dev libtool-bin \
    libxml-parser-perl make openssl p7zip-full patch perl \
    python3 python3-mako ruby scons sed unzip wget xz-utils

# Clone MXE repository
git clone https://github.com/mxe/mxe.git
cd mxe

# Build MXE with Qt6 and required dependencies
make MXE_TARGETS=x86_64-w64-mingw32.static \
    qtbase qttools ghostscript

# This will take some time to complete
```

### 2. Set up environment variables

```bash
# Add MXE binaries to your PATH
export PATH="$PATH:$(pwd)/usr/bin"
```

### 3. Build QPDFTools

```bash
# Navigate to your QPDFTools source directory
cd /path/to/qpdftools

# Configure with CMake using MXE's toolchain
x86_64-w64-mingw32.static-cmake -B build-windows -S . \
    -DCMAKE_BUILD_TYPE=Release

# Build
cmake --build build-windows --config Release

# Package
cd build-windows
cpack -G ZIP
```

## Method 2: Using Docker with MXE

For a more isolated and reproducible build environment, you can use Docker:

### 1. Create a Dockerfile

Create a file named `Dockerfile` with the following content:

```dockerfile
FROM ubuntu:22.04

# Install basic dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    python3 \
    python3-pip \
    wget \
    autoconf \
    automake \
    autopoint \
    bash \
    bison \
    bzip2 \
    flex \
    g++ \
    g++-multilib \
    gettext \
    gperf \
    intltool \
    libc6-dev-i386 \
    libgdk-pixbuf2.0-dev \
    libltdl-dev \
    libssl-dev \
    libtool-bin \
    libxml-parser-perl \
    make \
    openssl \
    p7zip-full \
    patch \
    perl \
    python3-mako \
    ruby \
    scons \
    sed \
    unzip \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

# Clone and build MXE
WORKDIR /opt
RUN git clone https://github.com/mxe/mxe.git
WORKDIR /opt/mxe
RUN make MXE_TARGETS=x86_64-w64-mingw32.static qtbase qttools ghostscript

# Set up environment
ENV PATH="/opt/mxe/usr/bin:${PATH}"

# Working directory for building
WORKDIR /src
```

### 2. Build the Docker image

```bash
docker build -t qpdftools-cross-compile .
```

### 3. Build QPDFTools using the Docker container

```bash
# Run the container with your source code mounted
docker run -it --rm -v $(pwd):/src qpdftools-cross-compile bash

# Inside the container
x86_64-w64-mingw32.static-cmake -B build-windows -S . \
    -DCMAKE_BUILD_TYPE=Release
cmake --build build-windows --config Release
cd build-windows
cpack -G ZIP
```

## Method 3: Using MinGW directly

For a simpler approach, you can use MinGW directly:

### 1. Install MinGW

```bash
sudo apt-get install -y mingw-w64
```

### 2. Install Qt for MinGW using aqtinstall

```bash
pip install aqtinstall
aqt install-qt linux desktop 6.2.4 win64_mingw
```

### 3. Build QPDFTools

```bash
# Set up environment variables
export CMAKE_PREFIX_PATH="$HOME/Qt/6.2.4/mingw_64"

# Configure with CMake
cmake -B build-windows -S . \
    -DCMAKE_TOOLCHAIN_FILE=<path-to-mingw-toolchain-file> \
    -DCMAKE_BUILD_TYPE=Release

# Build
cmake --build build-windows --config Release
```

## Notes

1. You'll need to ensure that the Windows versions of Ghostscript and QPDF are available during the build process.
2. Cross-compilation can be complex, and you might need to adjust paths and configurations based on your specific setup.
3. The MXE method is generally the most reliable for complex Qt applications.

## Troubleshooting

- If you encounter issues with finding Qt components, make sure the paths are correctly set in your environment.
- For dependency issues, you may need to manually build and install Windows versions of libraries.
- Check that the MinGW version matches the Qt build you're using.