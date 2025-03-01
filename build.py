#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import argparse
import shutil

def main():
    parser = argparse.ArgumentParser(description='Build QPDFTools')
    parser.add_argument('--platform', choices=['auto', 'windows', 'linux'], default='auto',
                        help='Target platform (default: auto-detect)')
    parser.add_argument('--type', choices=['debug', 'release'], default='release',
                        help='Build type (default: release)')
    parser.add_argument('--package', action='store_true',
                        help='Create installation package')
    parser.add_argument('--portable', action='store_true',
                        help='Create portable package (Windows only)')
    args = parser.parse_args()
    
    # Determine platform
    target_platform = args.platform
    if target_platform == 'auto':
        target_platform = 'windows' if platform.system() == 'Windows' else 'linux'
    
    # Set build type
    build_type = 'Release' if args.type == 'release' else 'Debug'
    
    # Create build directory
    build_dir = 'build'
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    
    # Configure CMake
    cmake_args = ['-DCMAKE_BUILD_TYPE=' + build_type]
    
    if target_platform == 'windows':
        # Windows-specific configuration
        if 'VSINSTALLDIR' in os.environ:
            # Visual Studio environment is already set up
            pass
        else:
            # Use default generator
            cmake_args.append('-G')
            cmake_args.append('Visual Studio 17 2022')
    
    # Run CMake configure
    cmake_configure_cmd = ['cmake', '-B', build_dir, '-S', '.'] + cmake_args
    print('Running:', ' '.join(cmake_configure_cmd))
    subprocess.run(cmake_configure_cmd, check=True)
    
    # Build
    cmake_build_cmd = ['cmake', '--build', build_dir, '--config', build_type]
    print('Running:', ' '.join(cmake_build_cmd))
    subprocess.run(cmake_build_cmd, check=True)
    
    # Package if requested
    if args.package or args.portable:
        # Create dist directory
        dist_dir = 'dist'
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)
        os.makedirs(dist_dir)
        
        # Install to dist directory
        cmake_install_cmd = ['cmake', '--install', build_dir, '--prefix', dist_dir]
        if target_platform == 'windows' and build_type != 'Debug':
            cmake_install_cmd.append('--strip')
        print('Running:', ' '.join(cmake_install_cmd))
        subprocess.run(cmake_install_cmd, check=True)
        
        if target_platform == 'windows':
            if args.package:
                # Create installer using CPack
                cpack_cmd = ['cpack', '-G', 'NSIS', '-C', build_type, '-B', 'installer']
                print('Running:', ' '.join(cpack_cmd))
                subprocess.run(cpack_cmd, cwd=build_dir, check=True)
                
                # Copy installer to project root
                installer_files = [f for f in os.listdir(os.path.join(build_dir, 'installer')) if f.endswith('.exe')]
                if installer_files:
                    shutil.copy(
                        os.path.join(build_dir, 'installer', installer_files[0]),
                        os.path.join('.', installer_files[0])
                    )
                    print(f'Installer created: {installer_files[0]}')
            
            if args.portable:
                # Create ZIP archive for portable use
                import zipfile
                zip_name = f'qpdftools-{target_platform}-portable.zip'
                with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, _, files in os.walk(dist_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(
                                file_path,
                                os.path.relpath(file_path, dist_dir)
                            )
                print(f'Portable package created: {zip_name}')

if __name__ == '__main__':
    main()