#pragma once

#include <QDebug>
#include <QException>
#include <QProcess>
#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QApplication>

class ExternalSoftware {
protected:
  QString softwareName;
  QString softwareCommand;

  void run(const QStringList &arguments, const QString &dir = "default");

public:
  ExternalSoftware(QString name, QString command);
  
  // Method to get platform-specific command path
  static QString getPlatformSpecificPath(const QString &baseCommand, const QString &windowsExeName);
};
