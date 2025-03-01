# Dependencies for QPDFTools

This directory contains dependencies required by QPDFTools on Windows.

## Required Dependencies

### Ghostscript

1. Download Ghostscript for Windows from https://www.ghostscript.com/download/gsdnld.html
2. Extract the files
3. Copy the following files to the `ghostscript/bin` directory:
   - gswin64c.exe
   - gsdll64.dll
   - All other required DLLs

### QPDF

1. Download QPDF for Windows from https://github.com/qpdf/qpdf/releases
2. Extract the files
3. Copy the following files to the `qpdf/bin` directory:
   - qpdf.exe
   - All required DLLs

## Directory Structure

```
deps/
  ├── ghostscript/
  │   └── bin/
  │       ├── gswin64c.exe
  │       ├── gsdll64.dll
  │       └── ... (other DLLs)
  └── qpdf/
      └── bin/
          ├── qpdf.exe
          └── ... (other DLLs)
```

## Usage

These dependencies are automatically used by QPDFTools on Windows. The application will look for these dependencies in the `deps` directory next to the executable.