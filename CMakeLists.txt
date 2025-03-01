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