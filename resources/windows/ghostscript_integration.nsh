; NSIS include file for Ghostscript integration

!define GS_INSTALLER_NAME "gs-installer.exe"
!define GS_SILENT_ARGS "/S /D=C:\Program Files\gs"

; Function to check if Ghostscript is installed
Function CheckGhostscriptInstalled
  IfFileExists "C:\Program Files\gs\bin\gswin64c.exe" 0 NotInstalled
    ; Ghostscript is installed
    Return
  NotInstalled:
    ; Ghostscript not installed, install it
    Call InstallGhostscript
FunctionEnd

; Function to install Ghostscript
Function InstallGhostscript
  DetailPrint "Installing Ghostscript..."
  
  ; Check if the Ghostscript installer is in the same directory as the main installer
  IfFileExists "$EXEDIR\${GS_INSTALLER_NAME}" 0 NoGSInstaller
    ; Found Ghostscript installer, run it silently
    ExecWait '"$EXEDIR\${GS_INSTALLER_NAME}" ${GS_SILENT_ARGS}'
    Goto GSDone
    
  NoGSInstaller:
    ; Check if Ghostscript installer is embedded in the installer
    IfFileExists "$INSTDIR\${GS_INSTALLER_NAME}" 0 NoGSEmbedded
      ; Found embedded Ghostscript installer, run it silently
      ExecWait '"$INSTDIR\${GS_INSTALLER_NAME}" ${GS_SILENT_ARGS}'
      Goto GSDone
      
  NoGSEmbedded:
    ; Installer not found, show a message
    MessageBox MB_OK|MB_ICONEXCLAMATION "Ghostscript installer not found. Please install Ghostscript manually."
    
  GSDone:
    ; Check if installation was successful
    IfFileExists "C:\Program Files\gs\bin\gswin64c.exe" GSSuccess GSFailed
    
  GSSuccess:
    DetailPrint "Ghostscript installed successfully."
    Return
    
  GSFailed:
    DetailPrint "Ghostscript installation failed."
    MessageBox MB_OK|MB_ICONEXCLAMATION "Ghostscript installation failed. QPDFTools requires Ghostscript to function properly. Please install it manually."
FunctionEnd
