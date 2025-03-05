# QPDFTools Windows Build Implementation - Changelog

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

### Fixed
- Fixed GitHub Actions workflow by removing incorrect Qt module specifications that were causing build failures

### Added
- Created comprehensive guide for cross-compiling from Linux to Windows (windows_cross_compile.md)
  - Documented MXE-based cross-compilation method
  - Documented Docker-based cross-compilation method
  - Documented MinGW-based cross-compilation method

## [Future Improvements]
- Replace the placeholder icon file with an actual ICO file
- Add more features to the build script as needed
- Improve CI/CD workflow with additional testing steps
- Test and refine the cross-compilation process