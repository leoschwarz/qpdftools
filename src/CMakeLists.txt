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
    --no-opengl-sw
    \"$<TARGET_FILE:qpdftools>\"
    COMMENT "Running windeployqt..."
  )
endif()
