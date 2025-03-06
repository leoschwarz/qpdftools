#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import argparse
import shutil
import logging
from typing import List, Optional
import zipfile
import urllib.request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger('build')

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Build QPDFTools')
    parser.add_argument('--platform', choices=['auto', 'windows', 'linux'], default='auto',
                        help='Target platform (default: auto-detect)')
    parser.add_argument('--type', choices=['debug', 'release'], default='release',
                        help='Build type (default: release)')
    parser.add_argument('--package', action='store_true',
                        help='Create installation package')
    parser.add_argument('--portable', action='store_true',
                        help='Create portable package (Windows only)')
    parser.add_argument('--flatpak', action='store_true',
                        help='Build using Flatpak (Linux only)')
    args = parser.parse_args()
    
    # Determine platform
    target_platform = args.platform
    if target_platform == 'auto':
        target_platform = 'windows' if platform.system() == 'Windows' else 'linux'
    
    return args, target_platform

def run_command(cmd: List[str], cwd: Optional[str] = None, shell=False, **kwargs) -> None:
    """Execute a command with proper logging and error handling."""
    cmd_str = ' '.join(cmd)
    logger.info(f'Running: {cmd_str}')
    try:
        subprocess.run(cmd, check=True, cwd=cwd, shell=shell, **kwargs)
    except subprocess.CalledProcessError as e:
        logger.error(f'Command failed: {cmd_str}')
        logger.error(f'Error: {e}')
        sys.exit(1)

def create_directory(dir_path: str, clean: bool = False) -> None:
    """Create a directory, optionally removing it first if it exists."""
    if clean and os.path.exists(dir_path):
        logger.info(f'Cleaning directory: {dir_path}')
        shutil.rmtree(dir_path)
    
    if not os.path.exists(dir_path):
        logger.info(f'Creating directory: {dir_path}')
        os.makedirs(dir_path)

def configure_cmake(build_dir: str, build_type: str, target_platform: str) -> None:
    """Configure the project with CMake."""
    cmake_args = ['-DCMAKE_BUILD_TYPE=' + build_type]
    
    # Add platform-specific CMake arguments
    if target_platform == 'windows' and 'VSINSTALLDIR' not in os.environ:
        # Use default generator on Windows if not in a Visual Studio environment
        cmake_args.extend(['-G', 'Visual Studio 17 2022'])
    
    # Run CMake configure
    cmd = ['cmake', '-B', build_dir, '-S', '.'] + cmake_args
    run_command(cmd)

def build_project(build_dir: str, build_type: str) -> None:
    """Build the project using CMake."""
    cmd = ['cmake', '--build', build_dir, '--config', build_type]
    run_command(cmd)

def install_to_dist(build_dir: str, dist_dir: str, build_type: str, target_platform: str) -> None:
    """Install the built project to the distribution directory."""
    cmd = ['cmake', '--install', build_dir, '--prefix', dist_dir]
    
    # Strip binaries for release builds on Windows
    if target_platform == 'windows' and build_type != 'Debug':
        cmd.append('--strip')
    
    run_command(cmd)

def create_windows_installer(build_dir: str, build_type: str) -> None:
    """Create a Windows installer using CPack/NSIS."""
    # Create installer using CPack
    cpack_cmd = ['cpack', '-G', 'NSIS', '-C', build_type, '-B', 'installer']
    run_command(cpack_cmd, cwd=build_dir)
    
    # Copy installer to project root
    installer_dir = os.path.join(build_dir, 'installer')
    installer_files = [f for f in os.listdir(installer_dir) if f.endswith('.exe')]
    
    if installer_files:
        installer_path = os.path.join(installer_dir, installer_files[0])
        # Create installers directory if it doesn't exist
        create_directory('installers')
        # Copy to installers directory
        shutil.copy(installer_path, os.path.join('installers', installer_files[0]))
        logger.info(f'Installer created: installers/{installer_files[0]}')
    else:
        logger.warning('No installer file found')

def find_windeployqt() -> Optional[str]:
    """Find the windeployqt executable path."""
    # Check if we're in GitHub Actions environment
    if 'IQTA_TOOLS' in os.environ:
        # GitHub Actions specific paths
        possible_paths = [
            os.path.join(os.environ.get('IQTA_TOOLS', ''), 'Qt', '6.2.4', 'msvc2019_64', 'bin', 'windeployqt.exe'),
            '/Qt/6.2.4/msvc2019_64/bin/windeployqt.exe'  # Alternate path format seen in logs
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
    
    # Check Qt6_DIR
    qt_bin_dir = os.environ.get('Qt6_DIR', '')
    if qt_bin_dir and os.path.exists(os.path.join(qt_bin_dir, 'windeployqt.exe')):
        return os.path.join(qt_bin_dir, 'windeployqt.exe')
    
    # Search in PATH
    for path_dir in os.environ.get('PATH', '').split(os.pathsep):
        windeployqt_path = os.path.join(path_dir, 'windeployqt.exe')
        if os.path.exists(windeployqt_path):
            return windeployqt_path
    
    return None

def deploy_qt_dependencies(dist_dir: str) -> None:
    """Deploy Qt dependencies for Windows portable build."""
    # Find executable in dist directory
    exe_path = None
    for root, _, files in os.walk(dist_dir):
        for file in files:
            if file.endswith('.exe'):
                exe_path = os.path.join(root, file)
                break
        if exe_path:
            break
    
    if not exe_path:
        logger.warning('No executable found in dist directory')
        return
    
    # Find windeployqt
    windeployqt_path = find_windeployqt()
    if not windeployqt_path:
        logger.warning("Could not find windeployqt.exe, Qt dependencies may be missing")
        logger.debug("PATH environment variable: " + os.environ.get('PATH', ''))
        logger.debug("Qt6_DIR environment variable: " + os.environ.get('Qt6_DIR', ''))
        return
    
    logger.info(f"Found windeployqt at: {windeployqt_path}")
    windeployqt_cmd = [
        windeployqt_path,
        '--verbose', '0',
        '--no-compiler-runtime',
        '--no-opengl-sw',
        exe_path
    ]
    
    try:
        run_command(windeployqt_cmd)
        logger.info("Successfully deployed Qt dependencies")
    except subprocess.CalledProcessError as e:
        logger.warning(f"Failed to run windeployqt: {e}")
        logger.warning("Qt dependencies may be missing")

def create_portable_package(dist_dir: str, target_platform: str) -> None:
    """Create a portable package without zipping for Windows."""
    # For Windows, we'll create a better organized structure
    if target_platform == 'windows':
        portable_dir = 'portable'
        create_directory(portable_dir, clean=True)
        
        # Create bin directory in portable dir
        bin_dir = os.path.join(portable_dir, 'bin')
        create_directory(bin_dir)
        
        # Copy contents from dist directory to portable directory
        for item in os.listdir(dist_dir):
            source_path = os.path.join(dist_dir, item)
            dest_path = os.path.join(portable_dir, item)
            if os.path.isdir(source_path):
                shutil.copytree(source_path, dest_path)
            else:
                shutil.copy2(source_path, dest_path)
        
        # Extract qpdf.zip content to the bin directory
        if os.path.exists('qpdf.zip'):
            logger.info('Extracting QPDF dependencies to portable bin directory')
            with zipfile.ZipFile('qpdf.zip', 'r') as qpdf_zip:
                for file_info in qpdf_zip.infolist():
                    # Only extract files from qpdf-10.6.3/bin folder
                    if file_info.filename.startswith('qpdf-10.6.3/bin/'):
                        # Extract directly to bin directory
                        target_path = os.path.join(bin_dir, os.path.basename(file_info.filename))
                        if not file_info.filename.endswith('/'):  # Skip directories
                            # Extract the file
                            extracted_data = qpdf_zip.read(file_info.filename)
                            # Write the file
                            with open(target_path, 'wb') as outfile:
                                outfile.write(extracted_data)
                            logger.info(f'Extracted {os.path.basename(file_info.filename)} to bin directory')
        
        # Copy Ghostscript binaries if they exist in deps folder
        gs_source_dir = os.path.join('deps', 'ghostscript', 'bin')
        if os.path.exists(gs_source_dir):
            logger.info('Copying Ghostscript binaries to portable bin directory')
            for item in os.listdir(gs_source_dir):
                source_path = os.path.join(gs_source_dir, item)
                dest_path = os.path.join(bin_dir, item)
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(source_path, dest_path)
                    logger.info(f'Copied {item} to bin directory')
        
        # Create a readme file explaining how to use the portable version
        readme_path = os.path.join(portable_dir, 'README.txt')
        with open(readme_path, 'w') as f:
            f.write('QPDFTools Portable\n')
            f.write('=================\n\n')
            f.write('This is a portable version of QPDFTools with all dependencies included.\n\n')
            f.write('Usage:\n')
            f.write('1. Simply run the qpdftools.exe file directly.\n')
            f.write('2. Do not move any files from their current locations.\n')
            f.write('3. The bin directory contains required dependencies that must stay with the main executable.\n\n')
            f.write('If you encounter any issues, please report them on the GitHub repository:\n')
            f.write('https://github.com/silash35/qpdftools\n')
        
        logger.info(f'Created portable package in directory: {portable_dir}')
        
        # Move GS installer to installers folder
        if os.path.exists('gs-installer.exe'):
            create_directory('installers', clean=False)
            shutil.copy('gs-installer.exe', os.path.join('installers', 'gs-installer.exe'))
            logger.info('Moved Ghostscript installer to installers directory')
    else:
        # Linux portable packaging remains unchanged
        zip_name = f'qpdftools-{target_platform}-portable.zip'
        logger.info(f'Creating portable package: {zip_name}')
        
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(dist_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    archive_path = os.path.relpath(file_path, dist_dir)
                    zipf.write(file_path, archive_path)
        
        logger.info(f'Portable package created: {zip_name}')

def organize_windows_build():
    """Organize Windows build artifacts into a structured format."""
    logger.info('Organizing Windows build artifacts')
    
    # Create output directories
    create_directory('installers', clean=False)
    
    # Move installer files to installers directory
    for file in os.listdir('.'):
        if file.endswith('.exe') and file != 'gs-installer.exe':
            if not os.path.exists(os.path.join('installers', file)):
                shutil.move(file, os.path.join('installers', file))
                logger.info(f'Moved {file} to installers directory')
    
    # Move portable-zip file to portable directory if it exists
    if os.path.exists('qpdftools-windows-portable.zip') and os.path.isdir('portable'):
        logger.info('Removing existing qpdftools-windows-portable.zip as we now use the portable directory directly')
        os.remove('qpdftools-windows-portable.zip')

def build_flatpak() -> None:
    """Build the project using Flatpak."""
    logger.info('Building with Flatpak')
    
    # Download the manifest from Flathub
    manifest_url = "https://raw.githubusercontent.com/flathub/br.eng.silas.qpdftools/master/br.eng.silas.qpdftools.yml"
    temp_manifest = "tmp.yml"
    final_manifest = "br.eng.silas.qpdftools.yml"
    
    # Download manifest using standard library
    logger.info(f'Downloading manifest from {manifest_url}')
    try:
        urllib.request.urlretrieve(manifest_url, temp_manifest)
    except Exception as e:
        logger.error(f'Failed to download manifest: {e}')
        sys.exit(1)
    
    # Read the temporary manifest
    with open(temp_manifest, 'r') as temp_file:
        manifest_lines = temp_file.readlines()
    
    # Write manifest excluding the last 3 lines (which typically contain source information)
    with open(final_manifest, 'w') as manifest_file:
        # Write all but the last 3 lines
        manifest_file.writelines(manifest_lines[:-3])
        # Add local directory as source
        manifest_file.write('      - type: dir\n')
        manifest_file.write('        path: .\n')
    
    # Build and install the Flatpak
    run_command(['flatpak-builder', '--install-deps-from=flathub', '--install', 'build-dir', final_manifest, '--force-clean'])
    
    # Cleanup temporary files
    if os.path.exists(temp_manifest):
        os.remove(temp_manifest)
    
    logger.info('Flatpak build completed')

def package_project(args, build_dir: str, dist_dir: str, build_type: str, target_platform: str) -> None:
    """Package the project based on the requested package types."""
    if not (args.package or args.portable or args.flatpak):
        return
    
    # Handle Flatpak build separately
    if args.flatpak and target_platform == 'linux':
        build_flatpak()
        return
    
    # Create and clean dist directory
    create_directory(dist_dir, clean=True)
    
    # Install to dist directory
    install_to_dist(build_dir, dist_dir, build_type, target_platform)
    
    # Create installer if requested (Windows only)
    if args.package and target_platform == 'windows':
        create_windows_installer(build_dir, build_type)
    
    # Create portable package if requested
    if args.portable:
        # For Windows, deploy Qt dependencies first
        if target_platform == 'windows':
            deploy_qt_dependencies(dist_dir)
        
        create_portable_package(dist_dir, target_platform)
    
    # For Windows, organize the build artifacts
    if target_platform == 'windows':
        organize_windows_build()

def main():
    """Main build function."""
    args, target_platform = parse_arguments()
    
    # Set build type
    build_type = 'Release' if args.type == 'release' else 'Debug'
    logger.info(f'Building for platform: {target_platform}, type: {build_type}')
    
    # Define directories
    build_dir = 'build'
    dist_dir = 'dist'
    
    # Create build directory
    create_directory(build_dir)
    
    # Configure, build and package
    configure_cmake(build_dir, build_type, target_platform)
    build_project(build_dir, build_type)
    package_project(args, build_dir, dist_dir, build_type, target_platform)
    
    logger.info('Build completed successfully!')

if __name__ == '__main__':
    main()