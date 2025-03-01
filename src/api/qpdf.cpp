#include "qpdf.hpp"

Qpdf::Qpdf()
    : ExternalSoftware("qpdf",
                      getPlatformSpecificPath("qpdf", "qpdf/bin/qpdf.exe")) {}

void Qpdf::splitPDF(const QString &input, const QString &outputFolder) {
  // qpdf in.pdf out.pdf --split-pages

  QStringList arguments;
  arguments << input << "out.pdf"
            << "--split-pages";

  run(arguments, outputFolder);
}

void Qpdf::splitPDF(const QString &input, const QString &output, int firstPage, int lastPage) {
  // qpdf in.pdf --pages . start-end -- out.pdf

  QStringList arguments;
  arguments << input << "--pages"
            << ".";
  arguments << QString::number(firstPage) + "-" + QString::number(lastPage);
  arguments << "--" << output;

  run(arguments);
}

void Qpdf::mergePDF(const QStringList &inputs, const QString &output) {
  // qpdf --empty --pages in1.pdf in2.pdf -- out.pdf
  QStringList arguments;

  arguments << "--empty"
            << "--pages";

  for (int i = 0; i < inputs.size(); ++i)
    arguments << inputs[i];

  arguments << "--" << output;

  run(arguments);
}

void Qpdf::rotatePDF(const QString &input, const QString &output, int angle) {
  // qpdf in.pdf out.pdf --rotate=angle

  QStringList arguments;

  arguments << input;
  arguments << output;
  arguments << "--rotate=" + QString::number(angle);

  run(arguments);
}

Qpdf qpdf;