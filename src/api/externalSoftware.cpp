#include "externalSoftware.hpp"

ExternalSoftware::ExternalSoftware(QString name, QString command)
    : softwareName(name), softwareCommand(command) {}

void ExternalSoftware::run(const QStringList &arguments, const QString &dir) {
  QProcess process;

  if (dir != "default") {
    process.setWorkingDirectory(dir);
    qInfo() << "Working directory:" << dir;
  }
  
  qInfo() << "Starting to execute" << softwareName << "(" << softwareCommand << ")"
          << "with arguments:" << arguments;
          
  // Check if the command exists
  if (!QFile::exists(softwareCommand) && !softwareCommand.contains("/") && !softwareCommand.contains("\\")) {
    qInfo() << "Command not found as a direct path, will try to find it in PATH";
  }
  
  process.start(softwareCommand, arguments, QIODevice::ReadWrite);
  process.closeWriteChannel();

  if (!process.waitForStarted(5000)) {
    QString errorMsg = "Failed to start " + softwareName + ": " + process.errorString();
    qCritical() << errorMsg;
    throw errorMsg.toStdString().c_str();
  }

  if (!process.waitForFinished(-1)) {
    QString errorMsg = "Process " + softwareName + " failed to finish: " + process.errorString();
    qCritical() << errorMsg;
    throw errorMsg.toStdString().c_str();
  }
  
  QString output = process.readAllStandardOutput();
  if (!output.isEmpty()) {
    qInfo() << "Output from" << softwareName << ":" << output;
  }
  
  qInfo() << "Finished executing" << softwareName;

  QString error = process.readAllStandardError();
  if (!error.isEmpty()) {
    qCritical() << "Error in" << softwareName << ":" << error;
    throw ("Error in " + softwareName + ": " + error).toStdString().c_str();
  }
  
  if (process.exitCode() != 0) {
    QString errorMsg = softwareName + " exited with code " + QString::number(process.exitCode());
    qCritical() << errorMsg;
    throw errorMsg.toStdString().c_str();
  }
}

QString ExternalSoftware::getPlatformSpecificPath(const QString &baseCommand, const QString &windowsExeName) {
#ifdef _WIN32
  // On Windows, look for the executable in multiple locations
  QString exePath;
  
  // Check if QApplication is initialized
  if (qApp) {
    exePath = QCoreApplication::applicationDirPath();
  } else {
    // If QApplication is not initialized, use the current directory
    exePath = QDir::currentPath();
    qWarning() << "QApplication not initialized when getting path for " << baseCommand
               << ". Using current directory instead.";
  }
  
  // List of locations to search for the executable in order of priority
  QStringList searchPaths = {
    // 1. Check in the 'bin' subdirectory of app directory (for portable setup)
    exePath + "/bin/" + baseCommand + ".exe",
    exePath + "/bin/gswin64c.exe", // Special case for Ghostscript
    
    // 2. Check directly in the app directory
    exePath + "/" + baseCommand + ".exe",
    exePath + "/" + windowsExeName,
    
    // 3. Check in the 'deps' directory structure (original path)
    exePath + "/deps/" + windowsExeName,
    
    // 4. Check relative paths without the 'deps' prefix
    exePath + "/" + windowsExeName.split("deps/").last()
  };
  
  // Log the search paths for debugging
  qInfo() << "Searching for" << baseCommand << "in the following locations:";
  for (const QString &path : searchPaths) {
    qInfo() << "  - " << path;
    if (QFile::exists(path)) {
      qInfo() << "Found " << baseCommand << " at " << path;
      return path;
    }
  }
  
  // If not found in any of the specified locations, return the base command (might be in PATH)
  qInfo() << "Could not find " << baseCommand << " in any of the specified locations. Using from PATH.";
  return baseCommand;
#else
  // On other platforms, just use the base command
  return baseCommand;
#endif
}
