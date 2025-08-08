"""
HoneyNet Desktop Build Script
סקריפט בנייה לדסקטופ של HoneyNet
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

class DesktopBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        
    def clean_build(self):
        """ניקוי תיקיות בנייה קודמות"""
        print("🧹 Cleaning previous builds...")
        for dir_path in [self.build_dir, self.dist_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
        print("✅ Build directories cleaned")
        
    def install_dependencies(self):
        """התקנת תלויות נדרשות לבנייה"""
        print("📦 Installing build dependencies...")
        dependencies = [
            "pyinstaller>=6.0.0",
            "auto-py-to-exe>=2.40.0",
            "pillow>=10.0.0",
            "requests>=2.31.0"
        ]
        
        for dep in dependencies:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                             check=True, capture_output=True)
                print(f"✅ Installed {dep}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {dep}: {e}")
                return False
        return True
        
    def create_spec_file(self):
        """יצירת קובץ spec עבור PyInstaller"""
        spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

# Project paths
project_root = Path(r"{self.project_root}")
i18n_path = project_root / "i18n"
assets_path = project_root / "assets"

a = Analysis(
    [str(project_root / "launch_desktop.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(i18n_path), "i18n"),
        (str(assets_path), "assets") if assets_path.exists() else None,
        (str(project_root / "README.md"), "."),
        (str(project_root / "LICENSE"), ".") if (project_root / "LICENSE").exists() else None,
    ],
    hiddenimports=[
        "tkinter",
        "tkinter.ttk",
        "tkinter.messagebox",
        "requests",
        "json",
        "threading",
        "datetime",
        "i18n",
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        "matplotlib",
        "scipy",
        "pandas",
        "jupyter",
        "IPython",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Filter out None values from datas
a.datas = [item for item in a.datas if item is not None]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="HoneyNet",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(assets_path / "icons" / "honeynet.ico") if (assets_path / "icons" / "honeynet.ico").exists() else None,
    version_file=None,
)
'''
        
        spec_file = self.project_root / "HoneyNet.spec"
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content.strip())
        
        print(f"✅ Created spec file: {spec_file}")
        return spec_file
        
    def create_assets(self):
        """יצירת נכסים נדרשים"""
        print("🎨 Creating assets...")
        
        # Create assets directory
        assets_dir = self.project_root / "assets"
        icons_dir = assets_dir / "icons"
        icons_dir.mkdir(parents=True, exist_ok=True)
        
        # Create simple icon (placeholder)
        try:
            from PIL import Image, ImageDraw
            
            # Create a simple icon
            img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Draw shield shape
            draw.ellipse([20, 20, 236, 236], fill=(0, 255, 0, 255), outline=(0, 150, 0, 255), width=4)
            draw.text((128, 128), "🛡️", anchor="mm", fill=(255, 255, 255, 255))
            
            # Save as PNG and ICO
            img.save(icons_dir / "honeynet.png")
            img.save(icons_dir / "honeynet.ico")
            
            print("✅ Created application icons")
            
        except ImportError:
            print("⚠️ PIL not available, skipping icon creation")
            
        # Create desktop file for Linux
        desktop_content = f'''[Desktop Entry]
Name=HoneyNet
Comment=Global Cyber Defense Platform
Comment[he]=פלטפורמת הגנה סייברית גלובלית
Comment[ar]=منصة الدفاع السيبراني العالمية
Exec={self.dist_dir / "HoneyNet"}
Icon=honeynet
Terminal=false
Type=Application
Categories=Network;Security;
StartupNotify=true
'''
        
        with open(assets_dir / "honeynet.desktop", 'w', encoding='utf-8') as f:
            f.write(desktop_content.strip())
            
        print("✅ Created desktop file")
        
    def build_executable(self):
        """בניית קובץ ההפעלה"""
        print("🔨 Building executable...")
        
        spec_file = self.create_spec_file()
        
        try:
            # Run PyInstaller
            cmd = [sys.executable, "-m", "PyInstaller", "--clean", str(spec_file)]
            result = subprocess.run(cmd, cwd=self.project_root, check=True, 
                                  capture_output=True, text=True)
            
            print("✅ Executable built successfully")
            print(f"📁 Output directory: {self.dist_dir}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed: {e}")
            print(f"Error output: {e.stderr}")
            return False
            
    def create_installer(self):
        """יצירת קובץ התקנה"""
        print("📦 Creating installer...")
        
        # Create NSIS installer script for Windows
        if sys.platform == "win32":
            self.create_windows_installer()
        else:
            self.create_linux_package()
            
    def create_windows_installer(self):
        """יצירת מתקין Windows"""
        nsis_script = f'''
!define APP_NAME "HoneyNet"
!define APP_VERSION "2.0.0"
!define APP_PUBLISHER "HoneyNet Global Team"
!define APP_URL "https://honeynet.global"
!define APP_EXECUTABLE "HoneyNet.exe"

!include "MUI2.nsh"

Name "${{APP_NAME}}"
OutFile "HoneyNet-Setup-v${{APP_VERSION}}.exe"
InstallDir "$PROGRAMFILES64\\${{APP_NAME}}"
InstallDirRegKey HKCU "Software\\${{APP_NAME}}" ""
RequestExecutionLevel admin

!define MUI_ABORTWARNING
!define MUI_ICON "assets\\icons\\honeynet.ico"
!define MUI_UNICON "assets\\icons\\honeynet.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Hebrew"
!insertmacro MUI_LANGUAGE "Arabic"

Section "Main Application" SecMain
    SetOutPath "$INSTDIR"
    File /r "dist\\HoneyNet\\*.*"
    
    CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXECUTABLE}}"
    CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXECUTABLE}}"
    
    WriteRegStr HKCU "Software\\${{APP_NAME}}" "" $INSTDIR
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\Uninstall.exe"
    RMDir /r "$INSTDIR"
    Delete "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk"
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"
    RMDir "$SMPROGRAMS\\${{APP_NAME}}"
    DeleteRegKey HKCU "Software\\${{APP_NAME}}"
SectionEnd
'''
        
        with open(self.project_root / "installer.nsi", 'w', encoding='utf-8') as f:
            f.write(nsis_script.strip())
            
        print("✅ Created Windows installer script")
        print("ℹ️ Run 'makensis installer.nsi' to create the installer")
        
    def create_linux_package(self):
        """יצירת חבילה ללינוקס"""
        print("🐧 Creating Linux package...")
        
        # Create AppImage structure
        appdir = self.build_dir / "HoneyNet.AppDir"
        appdir.mkdir(parents=True, exist_ok=True)
        
        # Copy executable
        shutil.copytree(self.dist_dir / "HoneyNet", appdir / "usr" / "bin", dirs_exist_ok=True)
        
        # Create AppRun script
        apprun_content = '''#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
exec "${HERE}/usr/bin/HoneyNet" "$@"
'''
        
        apprun_file = appdir / "AppRun"
        with open(apprun_file, 'w') as f:
            f.write(apprun_content)
        os.chmod(apprun_file, 0o755)
        
        print("✅ Created Linux AppImage structure")
        
    def build_all(self):
        """בנייה מלאה"""
        print("🚀 Starting HoneyNet Desktop build process...")
        
        if not self.install_dependencies():
            return False
            
        self.clean_build()
        self.create_assets()
        
        if not self.build_executable():
            return False
            
        self.create_installer()
        
        print("🎉 Build completed successfully!")
        print(f"📁 Executable: {self.dist_dir / 'HoneyNet'}")
        
        return True

def main():
    """נקודת כניסה ראשית"""
    builder = DesktopBuilder()
    success = builder.build_all()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
