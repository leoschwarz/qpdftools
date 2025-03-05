#include "interface/mainwindow.hpp"
#include <QApplication>
#include <QStyleHints>
#include <QTranslator>
#include <QtGlobal>

// Qt::ColorScheme was introduced in Qt 6.5
// For compatibility with Qt 6.2.4, we create our own enum
#if QT_VERSION < QT_VERSION_CHECK(6, 5, 0)
namespace Qt {
    enum class ColorScheme {
        Unknown,
        Light,
        Dark
    };
}
#endif

Qt::ColorScheme getColorScheme(int windowColor, int windowTextColor);

int main(int argc, char *argv[]) {
  QApplication app(argc, argv);

  QApplication::setDesktopFileName("br.eng.silas.qpdftools");

  // Enable fallback icons, in case the theme doesn't provide them
  Qt::ColorScheme colorScheme = getColorScheme(app.palette().window().color().value(),
                                               app.palette().windowText().color().value());
  QString fallbackIcons =
      colorScheme == Qt::ColorScheme::Dark ? ":/fallback-icons-dark" : ":/fallback-icons-light";
  QIcon::setFallbackSearchPaths(QIcon::fallbackSearchPaths() << fallbackIcons);
  
  // On Windows, we need to explicitly set the theme icons since Windows doesn't have a standard icon theme
#ifdef _WIN32
  QIcon::setThemeName("fallback");
  QIcon::setThemeSearchPaths(QStringList() << ":/");
#endif

  // Enable Translations for other languages
  // Search available translations with this format :/i18n/qpdftools_pt_BR.qm
  QTranslator translator;
  if (translator.load(QLocale(), "qpdftools", "_", ":/i18n"))
    QCoreApplication::installTranslator(&translator);

  MainWindow w;
  w.show();
  return app.exec();
}

Qt::ColorScheme getColorScheme(int windowColor, int windowTextColor) {
#if QT_VERSION >= QT_VERSION_CHECK(6, 5, 0)
  // Use the built-in Qt::ColorScheme if available (Qt 6.5+)
  if (Qt::ColorScheme() != Qt::ColorScheme::Unknown)
    return Qt::ColorScheme();
#endif

  // If the system doesn't support color schemes, find if it's light or dark
  // by comparing the color of the background and text.
  // if the background is lighter than the text, it's light, otherwise it's dark
  if (windowColor > windowTextColor)
    return Qt::ColorScheme::Light;

  return Qt::ColorScheme::Dark;
}