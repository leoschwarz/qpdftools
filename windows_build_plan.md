# Windows Build Plan for QPDFTools

This document provides step-by-step instructions for adding Windows build support to the QPDFTools project.

## Prerequisites

- CMake 3.16 or higher
- Qt6 development environment
- Visual Studio (for Windows builds)
- NSIS (for creating Windows installers)

## Step 1: Update CMake Configuration

### 1.1 Modify Main CMakeLists.txt

Open `CMakeLists.txt` in the project root and update it to handle platform-specific configurations:

```cmake
cmake_minimum_required(VERSION 3.16)
project(qpdftools VERSION 3.1.1)

set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Platform-specific configuration
if(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
  # Windows-specific configuration
  set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
  set(BUILD_SHARED_LIBS ON)
else()
  # Linux-specific configuration
  # Keep existing configuration
endif()

add_subdirectory(resources)
add_subdirectory(src)

# CPack configuration for installers
if(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
  set(CPACK_GENERATOR "NSIS")
  set(CPACK_PACKAGE_NAME "QPDFTools")
  set(CPACK_PACKAGE_VENDOR "Silas")
  set(CPACK_PACKAGE_VERSION "${PROJECT_VERSION}")
  set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "PDF manipulation tools")
  set(CPACK_PACKAGE_INSTALL_DIRECTORY "QPDFTools")
  include(CPack)
endif()
```

### 1.2 Update src/CMakeLists.txt

Modify `src/CMakeLists.txt` to handle platform-specific configurations:

```cmake
# Platform-specific configuration
if(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
  find_package(ECM REQUIRED NO_MODULE)
  set(CMAKE_MODULE_PATH ${ECM_MODULE_PATH})
  include(KDEInstallDirs)
endif()

# Add Qt
find_package(Qt6 REQUIRED COMPONENTS Widgets Concurrent LinguistTools)

# Common source files
set(SRC
  main.cpp

  ../resources/fallback-icons/fallback-icons.qrc

  api/externalSoftware.cpp
  api/ghostscript.cpp
  api/qpdf.cpp

  interface/mainwindow.ui
  interface/mainwindow.cpp

  interface/utils/fileDialog.cpp

  interface/pages/0-menu/menu.ui
  interface/pages/0-menu/menu.cpp
  interface/pages/1-compress/compress.ui
  interface/pages/1-compress/compress.cpp
  interface/pages/2-split/split.ui
  interface/pages/2-split/split.cpp
  interface/pages/3-merge/merge.ui
  interface/pages/3-merge/merge.cpp
  interface/pages/4-rotate/rotate.ui
  interface/pages/4-rotate/rotate.cpp
)

# Platform-specific source files
if(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
  set(SRC ${SRC} ../resources/windows/app.rc)
endif()

add_executable(qpdftools
  ${SRC}
)

set(TS_FILES languages/qpdftools_pt_BR.ts)
qt6_add_translations(qpdftools TS_FILES ${TS_FILES})

target_link_libraries(qpdftools
  PRIVATE
  Qt6::Core
  Qt6::Concurrent
  Qt6::Widgets
)

# Platform-specific installation
if(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
  install(TARGETS qpdftools DESTINATION ${KDE_INSTALL_BINDIR})
elseif(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
  install(TARGETS qpdftools DESTINATION .)
  
  # Install Qt DLLs
  get_target_property(_qmake_executable Qt6::qmake IMPORTED_LOCATION)
  get_filename_component(_qt_bin_dir "${_qmake_executable}" DIRECTORY)
  
  find_program(WINDEPLOYQT_EXECUTABLE windeployqt HINTS "${_qt_bin_dir}")
  add_custom_command(TARGET qpdftools POST_BUILD
    COMMAND "${CMAKE_COMMAND}" -E
    env PATH="${_qt_bin_dir}" "${WINDEPLOYQT_EXECUTABLE}"
    --verbose 0
    --no-compiler-runtime
    --no-angle
    --no-opengl-sw
    \"$<TARGET_FILE:qpdftools>\"
    COMMENT "Running windeployqt..."
  )
endif()
```

### 1.3 Update resources/CMakeLists.txt

Modify `resources/CMakeLists.txt` to handle platform-specific configurations:

```cmake
# Platform-specific configuration
if(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
  # Add ECM Modules
  find_package(ECM REQUIRED NO_MODULE)
  set(CMAKE_MODULE_PATH ${ECM_MODULE_PATH})
  include(ECMInstallIcons)
  include(KDEInstallDirs)
  
  set(ICONS
    icons/16-apps-br.eng.silas.qpdftools.png
    icons/22-apps-br.eng.silas.qpdftools.png
    icons/24-apps-br.eng.silas.qpdftools.png
    icons/32-apps-br.eng.silas.qpdftools.png
    icons/36-apps-br.eng.silas.qpdftools.png
    icons/48-apps-br.eng.silas.qpdftools.png
    icons/64-apps-br.eng.silas.qpdftools.png
    icons/72-apps-br.eng.silas.qpdftools.png
    icons/96-apps-br.eng.silas.qpdftools.png
    icons/128-apps-br.eng.silas.qpdftools.png
    icons/192-apps-br.eng.silas.qpdftools.png
    icons/256-apps-br.eng.silas.qpdftools.png
    icons/512-apps-br.eng.silas.qpdftools.png
    icons/sc-apps-br.eng.silas.qpdftools.svg
  )
  
  ecm_install_icons(ICONS ${ICONS}
    DESTINATION ${KDE_INSTALL_ICONDIR} THEME hicolor
  )
  
  install(PROGRAMS br.eng.silas.qpdftools.desktop DESTINATION ${KDE_INSTALL_APPDIR})
  install(FILES br.eng.silas.qpdftools.metainfo.xml DESTINATION ${KDE_INSTALL_METAINFODIR})
elseif(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
  # Windows-specific resource configuration
  # No special handling needed here as Windows resources are handled in src/CMakeLists.txt
endif()
```

## Step 2: Create Windows-Specific Resources

### 2.1 Create Windows Resource Directory

Create a new directory for Windows-specific resources:

```
mkdir -p resources/windows
```

### 2.2 Create Windows Resource File (app.rc)

Create `resources/windows/app.rc` with the following content:

```rc
#include <windows.h>

IDI_ICON1 ICON DISCARDABLE "app.ico"

VS_VERSION_INFO VERSIONINFO
FILEVERSION     3,1,1,0
PRODUCTVERSION  3,1,1,0
BEGIN
    BLOCK "StringFileInfo"
    BEGIN
        BLOCK "040904E4"
        BEGIN
            VALUE "CompanyName",      "Silas"
            VALUE "FileDescription",  "PDF manipulation tools"
            VALUE "FileVersion",      "3.1.1"
            VALUE "InternalName",     "qpdftools"
            VALUE "LegalCopyright",   "Silas"
            VALUE "OriginalFilename", "qpdftools.exe"
            VALUE "ProductName",      "QPDFTools"
            VALUE "ProductVersion",   "3.1.1"
        END
    END
    BLOCK "VarFileInfo"
    BEGIN
        VALUE "Translation", 0x409, 1252
    END
END
```

### 2.3 Create Windows Icon File

Convert the existing SVG icon to ICO format and save it as `resources/windows/app.ico`:

```
# Use an SVG to ICO converter tool or online service
# Example command using ImageMagick:
convert resources/icons/sc-apps-br.eng.silas.qpdftools.svg -define icon:auto-resize=16,32,48,64,128,256 resources/windows/app.ico
```

## Step 3: Update External Tool Handling

### 3.1 Modify ExternalSoftware Class

Update `src/api/externalSoftware.hpp` to add platform-specific path handling:

```cpp
#pragma once

#include <QDebug>
#include <QException>
#include <QProcess>
#include <QCoreApplication>
#include <QDir>

class ExternalSoftware {
protected:
  QString softwareName;
  QString softwareCommand;

  void run(const QStringList &arguments, const QString &dir = "default");

public:
  ExternalSoftware(QString name, QString command);
  
  // New method to get platform-specific command path
  static QString getPlatformSpecificPath(const QString &baseCommand, const QString &windowsExeName);
};
```

### 3.2 Implement Platform-Specific Path Handling

Update `src/api/externalSoftware.cpp` to implement platform-specific path handling:

```cpp
#include "externalSoftware.hpp"

ExternalSoftware::ExternalSoftware(QString name, QString command)
    : softwareName(name), softwareCommand(command) {}

void ExternalSoftware::run(const QStringList &arguments, const QString &dir) {
  QProcess process;

  if (dir != "default") {
    process.setWorkingDirectory(dir);
    qInfo() << dir << "\n";
  }
  qInfo() << "starting to execute " << softwareName << " with the following arguments:" << arguments
          << "\n";
  process.start(softwareCommand, arguments, QIODevice::ReadWrite);
  process.closeWriteChannel();

  process.waitForFinished();
  qInfo() << "finished to execute " + softwareName << "\n";

  QString error = process.readAllStandardError();

  if (!error.isEmpty()) {
    qCritical() << "Error in " + softwareName + ": " + error << "\n";
    throw "Error in " + softwareName + ": " + error;
  }
}

QString ExternalSoftware::getPlatformSpecificPath(const QString &baseCommand, const QString &windowsExeName) {
#ifdef _WIN32
  // On Windows, look for the executable in the deps directory next to the application
  QString exePath = QCoreApplication::applicationDirPath();
  QString depsPath = exePath + "/deps";
  
  // First check if the tool is in the deps directory
  QString toolPath = depsPath + "/" + windowsExeName;
  if (QFile::exists(toolPath)) {
    return toolPath;
  }
  
  // If not found in deps, return the base command (might be in PATH)
  return baseCommand;
#else
  // On other platforms, just use the base command
  return baseCommand;
#endif
}
```

### 3.3 Update Ghostscript Class

Update `src/api/ghostscript.cpp` to use platform-specific paths:

```cpp
#include "ghostscript.hpp"

Ghostscript::Ghostscript() 
    : ExternalSoftware("Ghostscript", 
                      getPlatformSpecificPath("gs", "ghostscript/bin/gswin64c.exe")) {}

// Rest of the file remains unchanged
```

### 3.4 Update QPDF Class

Update `src/api/qpdf.cpp` to use platform-specific paths:

```cpp
#include "qpdf.hpp"

Qpdf::Qpdf() 
    : ExternalSoftware("qpdf", 
                      getPlatformSpecificPath("qpdf", "qpdf/bin/qpdf.exe")) {}

// Rest of the file remains unchanged
```

## Step 4: Create Dependencies Directory Structure

### 4.1 Create Directory Structure for Windows Dependencies

Create a directory structure for bundled dependencies:

```
mkdir -p deps/ghostscript/bin
mkdir -p deps/qpdf/bin
```

### 4.2 Add README for Dependencies

Create `deps/README.md` with instructions for adding dependencies:

```markdown
# Dependencies for QPDFTools

This directory contains dependencies required by QPDFTools on Windows.

## Required Dependencies

### Ghostscript

1. Download Ghostscript for Windows from https://www.ghostscript.com/download/gsdnld.html
2. Extract the files
3. Copy the following files to the `ghostscript/bin` directory:
   - gswin64c.exe
   - gsdll64.dll
   - All other required DLLs

### QPDF

1. Download QPDF for Windows from https://github.com/qpdf/qpdf/releases
2. Extract the files
3. Copy the following files to the `qpdf/bin` directory:
   - qpdf.exe
   - All required DLLs
```

## Step 5: Create Build Automation Script

### 5.1 Create Cross-Platform Build Script

Create `build.py` in the project root:

```python
#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import argparse
import shutil

def main():
    parser = argparse.ArgumentParser(description='Build QPDFTools')
    parser.add_argument('--platform', choices=['auto', 'windows', 'linux'], default='auto',
                        help='Target platform (default: auto-detect)')
    parser.add_argument('--type', choices=['debug', 'release'], default='release',
                        help='Build type (default: release)')
    parser.add_argument('--package', action='store_true',
                        help='Create installation package')
    parser.add_argument('--portable', action='store_true',
                        help='Create portable package (Windows only)')
    args = parser.parse_args()
    
    # Determine platform
    target_platform = args.platform
    if target_platform == 'auto':
        target_platform = 'windows' if platform.system() == 'Windows' else 'linux'
    
    # Set build type
    build_type = 'Release' if args.type == 'release' else 'Debug'
    
    # Create build directory
    build_dir = 'build'
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    
    # Configure CMake
    cmake_args = ['-DCMAKE_BUILD_TYPE=' + build_type]
    
    if target_platform == 'windows':
        # Windows-specific configuration
        if 'VSINSTALLDIR' in os.environ:
            # Visual Studio environment is already set up
            pass
        else:
            # Use default generator
            cmake_args.append('-G')
            cmake_args.append('Visual Studio 17 2022')
    
    # Run CMake configure
    cmake_configure_cmd = ['cmake', '-B', build_dir, '-S', '.'] + cmake_args
    print('Running:', ' '.join(cmake_configure_cmd))
    subprocess.run(cmake_configure_cmd, check=True)
    
    # Build
    cmake_build_cmd = ['cmake', '--build', build_dir, '--config', build_type]
    print('Running:', ' '.join(cmake_build_cmd))
    subprocess.run(cmake_build_cmd, check=True)
    
    # Package if requested
    if args.package or args.portable:
        # Create dist directory
        dist_dir = 'dist'
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)
        os.makedirs(dist_dir)
        
        # Install to dist directory
        cmake_install_cmd = ['cmake', '--install', build_dir, '--prefix', dist_dir]
        if target_platform == 'windows' and build_type != 'Debug':
            cmake_install_cmd.append('--strip')
        print('Running:', ' '.join(cmake_install_cmd))
        subprocess.run(cmake_install_cmd, check=True)
        
        if target_platform == 'windows':
            if args.package:
                # Create installer using CPack
                cpack_cmd = ['cpack', '-G', 'NSIS', '-C', build_type, '-B', 'installer']
                print('Running:', ' '.join(cpack_cmd))
                subprocess.run(cpack_cmd, cwd=build_dir, check=True)
                
                # Copy installer to project root
                installer_files = [f for f in os.listdir(os.path.join(build_dir, 'installer')) if f.endswith('.exe')]
                if installer_files:
                    shutil.copy(
                        os.path.join(build_dir, 'installer', installer_files[0]),
                        os.path.join('.', installer_files[0])
                    )
                    print(f'Installer created: {installer_files[0]}')
            
            if args.portable:
                # Create ZIP archive for portable use
                import zipfile
                zip_name = f'qpdftools-{target_platform}-portable.zip'
                with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, _, files in os.walk(dist_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(
                                file_path,
                                os.path.relpath(file_path, dist_dir)
                            )
                print(f'Portable package created: {zip_name}')

if __name__ == '__main__':
    main()
```

### 5.2 Make the Script Executable (Linux/macOS)

```bash
chmod +x build.py
```

## Step 6: Set Up CI/CD for Windows Builds

### 6.1 Create GitHub Actions Workflow

Create `.github/workflows/build.yml`:

```yaml
name: Build

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'
      
      - name: Install Qt
        uses: jurplel/install-qt-action@v2
        with:
          version: '6.2.4'
          host: 'windows'
          target: 'desktop'
          arch: 'win64_msvc2019_64'
          modules: 'qtwidgets qtconcurrent'
      
      - name: Download Ghostscript
        run: |
          Invoke-WebRequest -Uri "https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs1000/gs1000w64.exe" -OutFile "gs-installer.exe"
          Start-Process -FilePath "gs-installer.exe" -ArgumentList "/S /D=C:\ghostscript" -Wait
          mkdir -p deps/ghostscript/bin
          Copy-Item "C:\ghostscript\bin\*" -Destination "deps/ghostscript/bin" -Recurse
      
      - name: Download QPDF
        run: |
          Invoke-WebRequest -Uri "https://github.com/qpdf/qpdf/releases/download/release-qpdf-10.6.3/qpdf-10.6.3-bin-mingw64.zip" -OutFile "qpdf.zip"
          Expand-Archive -Path "qpdf.zip" -DestinationPath "C:\qpdf"
          mkdir -p deps/qpdf/bin
          Copy-Item "C:\qpdf\qpdf-10.6.3\bin\*" -Destination "deps/qpdf/bin" -Recurse
      
      - name: Build
        run: |
          python build.py --platform windows --type release
      
      - name: Create Package
        run: |
          python build.py --platform windows --type release --package --portable
      
      - name: Upload Artifacts
        uses: actions/upload-artifact@v2
        with:
          name: windows-build
          path: |
            *.exe
            *.zip
  
  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install Dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y build-essential cmake extra-cmake-modules qtbase5-dev libqt5concurrent5 qt5-qmake qttools5-dev-tools ghostscript qpdf
      
      - name: Build
        run: |
          python3 build.py --platform linux --type release
      
      - name: Create Package
        run: |
          python3 build.py --platform linux --type release --package
      
      - name: Upload Artifacts
        uses: actions/upload-artifact@v2
        with:
          name: linux-build
          path: dist/
```

## Step 7: Testing the Windows Build

### 7.1 Local Testing

1. Install prerequisites:
   - CMake
   - Qt6
   - Visual Studio
   - Python 3

2. Download and install dependencies:
   - Ghostscript for Windows
   - QPDF for Windows

3. Copy dependencies to the `deps` directory as described in the README

4. Run the build script:
   ```
   python build.py --platform windows --type release
   ```

5. Test the application:
   ```
   build\Release\qpdftools.exe
   ```

### 7.2 Creating Packages

1. Create an installer:
   ```
   python build.py --platform windows --type release --package
   ```

2. Create a portable package:
   ```
   python build.py --platform windows --type release --portable
   ```

## Conclusion

This plan provides a step-by-step approach to adding Windows build support to QPDFTools. By following these instructions, you can create Windows builds while maintaining Linux compatibility.

The key components of this plan are:
1. Platform-specific CMake configuration
2. Windows resource files
3. External dependency management
4. Build automation script
5. CI/CD integration

This approach ensures that the build system remains simple while supporting multiple platforms effectively.