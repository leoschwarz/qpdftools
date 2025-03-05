# QPDFTools Cross-Platform Build Implementation - Changelog

## [Unreleased]
### Added
- Initial setup of CRCT system files for tracking the Windows build implementation
- Updated CMakeLists.txt with Windows-specific configuration and CPack support
- Updated src/CMakeLists.txt with Windows-specific build and installation rules
- Updated resources/CMakeLists.txt with platform-specific conditional blocks
- Created Windows resource directory (resources/windows)
- Created Windows resource file (app.rc)
- Created placeholder for Windows icon file (app.ico)
- Updated ExternalSoftware class with platform-specific path handling
- Updated Ghostscript and QPDF classes to use platform-specific paths
- Created dependencies directory structure for Windows builds
- Added README for dependencies
- Created build automation script (build.py) for cross-platform builds
- Set up CI/CD configuration for Windows builds using GitHub Actions
- Created comprehensive guide for cross-compiling from Linux to Windows (windows_cross_compile.md)
  - Documented MXE-based cross-compilation method
  - Documented Docker-based cross-compilation method
  - Documented MinGW-based cross-compilation method
- Created bash script (generate_ico.sh) to generate Windows icon file from SVG source
- Generated and committed Windows icon file (app.ico) to simplify the build process

### Fixed
- Fixed GitHub Actions workflow by removing incorrect Qt module specifications that were causing build failures
- Fixed Windows build compatibility issue with Qt::ColorScheme by adding a fallback implementation for Qt 6.2.4
- Fixed Windows build failure in GitHub Actions by adding automatic generation of app.ico from SVG source
- Simplified GitHub Actions workflow by removing ImageMagick dependency and using pre-generated icon file
- Fixed Linux build in GitHub Actions by updating the workflow to use Qt6 instead of Qt5
- Fixed Windows build issue with missing Qt6Core.dll by improving Qt dependency deployment
- Fixed Windows build error with qpdf variable declaration mismatch (type 'Qpdf &' vs 'Qpdf')

### Issues
- Identified issue with Windows build in GitHub Actions: windeployqt tool fails with "Unknown option 'no-angle'" error
- Fixed windeployqt error by explicitly removing the unsupported `--no-angle` option and adding a comment explaining the removal
- Identified issue with Linux build in GitHub Actions: CMake couldn't find Qt6 because the workflow was installing Qt5
- Fixed Linux build by updating the GitHub Actions workflow to use the jurplel/install-qt-action@v3 action with Qt6
- Identified issue with Windows build: application fails to start with "Qt6Core.dll not found" error
- Fixed Qt6Core.dll missing error by:
  - Enhancing build.py to run windeployqt on the installed executable when creating a portable package
  - Modifying src/CMakeLists.txt to run windeployqt during both post-build and installation
  - Updating GitHub workflow to ensure Qt bin directory is in PATH and setting Qt6_DIR environment variable
- Identified issue with Windows build in GitHub Actions: build fails with "FileNotFoundError" when trying to run windeployqt.exe
- Fixed windeployqt path detection issue by:
  - Enhancing build.py to search for windeployqt.exe in multiple possible locations, including GitHub Actions-specific paths
  - Adding detailed error reporting and path debugging to help diagnose path-related issues
  - Updating GitHub Actions workflow to include diagnostic steps that verify Qt installation paths
  - Adding support for alternate path formats that appear in GitHub Actions logs

## [Future Improvements]
- ✅ Replace the placeholder icon file with an actual ICO file (now pre-generated and committed to repository)
- Add more features to the build script as needed
- Improve CI/CD workflow with additional testing steps
- Test and refine the cross-compilation process