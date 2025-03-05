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
  // On Windows, look for the executable in the deps directory next to the application
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
  
  QString depsPath = exePath + "/deps";
  
  // First check if the tool is in the deps directory
  QString toolPath = depsPath + "/" + windowsExeName;
  if (QFile::exists(toolPath)) {
    qInfo() << "Found " << baseCommand << " at " << toolPath;
    return toolPath;
  }
  
  // Also check in the same directory as the application
  toolPath = exePath + "/" + windowsExeName;
  if (QFile::exists(toolPath)) {
    qInfo() << "Found " << baseCommand << " at " << toolPath;
    return toolPath;
  }
  
  // If not found in deps or app directory, return the base command (might be in PATH)
  qInfo() << "Using " << baseCommand << " from PATH";
  return baseCommand;
#else
  // On other platforms, just use the base command
  return baseCommand;
#endif
}
