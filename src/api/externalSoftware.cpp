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
