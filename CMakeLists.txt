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
  
  # Custom NSIS installer configuration
  set(CPACK_NSIS_MODIFY_PATH ON)
  set(CPACK_NSIS_MUI_ICON "${CMAKE_SOURCE_DIR}/resources/windows/app.ico")
  set(CPACK_NSIS_MUI_UNIICON "${CMAKE_SOURCE_DIR}/resources/windows/app.ico")
  set(CPACK_NSIS_INSTALLED_ICON_NAME "qpdftools.exe")
  set(CPACK_NSIS_HELP_LINK "https://github.com/silash35/qpdftools")
  set(CPACK_NSIS_URL_INFO_ABOUT "https://github.com/silash35/qpdftools")
  set(CPACK_NSIS_DISPLAY_NAME "QPDFTools ${PROJECT_VERSION}")
  
  # Include Ghostscript installer in the package if it exists
  if(EXISTS "${CMAKE_SOURCE_DIR}/gs-installer.exe")
    set(CPACK_PACKAGE_FILE_NAME "qpdftools-${PROJECT_VERSION}-windows-installer")
    install(FILES "${CMAKE_SOURCE_DIR}/gs-installer.exe" DESTINATION ".")
    
    # Add a simpler, direct NSIS code instead of including a file
    set(CPACK_NSIS_EXTRA_INSTALL_COMMANDS "
      ; Check for Ghostscript installation
      IfFileExists 'C:\\\\Program Files\\\\gs\\\\bin\\\\gswin64c.exe' GSAlreadyInstalled
        DetailPrint 'Installing Ghostscript...'
        IfFileExists '$INSTDIR\\\\gs-installer.exe' 0 GSNotFound
          ExecWait '\\\"$INSTDIR\\\\gs-installer.exe\\\" /S /D=C:\\\\Program Files\\\\gs'
          Goto GSCheck
        GSNotFound:
          MessageBox MB_OK|MB_ICONEXCLAMATION 'Ghostscript installer not found. Please install Ghostscript manually.'
      GSAlreadyInstalled:
        DetailPrint 'Ghostscript is already installed.'
      GSCheck:
        IfFileExists 'C:\\\\Program Files\\\\gs\\\\bin\\\\gswin64c.exe' 0 GSInstallFailed
        DetailPrint 'Ghostscript installation successful or already installed.'
        Goto GSInstallEnd
      GSInstallFailed:
        DetailPrint 'Ghostscript installation failed.'
        MessageBox MB_OK|MB_ICONEXCLAMATION 'Ghostscript installation failed. QPDFTools requires Ghostscript to function properly. Please install it manually.'
      GSInstallEnd:
    ")
  endif()
  
  include(CPack)
endif()