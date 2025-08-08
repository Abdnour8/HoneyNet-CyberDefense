@echo off
echo ========================================
echo   HoneyNet Android APK Builder
echo   Ze'ev Weinerich Technologies Ltd.
echo ========================================
echo.

echo 📱 Building HoneyNet Android APK...
echo.

REM Check if Android SDK is available
if not exist "%ANDROID_HOME%" (
    echo ❌ Android SDK not found!
    echo.
    echo Please install Android Studio and set ANDROID_HOME environment variable.
    echo Download from: https://developer.android.com/studio
    echo.
    echo Alternative: Use online APK builder
    echo 1. Go to: https://appsgeyser.com/
    echo 2. Choose "Website to App"
    echo 3. Enter URL: http://18.209.27.121
    echo 4. App Name: HoneyNet
    echo 5. Download APK
    echo.
    pause
    goto :end
)

echo ✅ Android SDK found: %ANDROID_HOME%
echo.

REM Create project structure
echo 📁 Creating Android project structure...
mkdir android_project\app\src\main\java\com\zeevweinerich\honeynet 2>nul
mkdir android_project\app\src\main\res\layout 2>nul
mkdir android_project\app\src\main\res\values 2>nul
mkdir android_project\app\src\main\res\mipmap-hdpi 2>nul
mkdir android_project\app\src\main\res\mipmap-mdpi 2>nul
mkdir android_project\app\src\main\res\mipmap-xhdpi 2>nul
mkdir android_project\app\src\main\res\mipmap-xxhdpi 2>nul
mkdir android_project\app\src\main\res\mipmap-xxxhdpi 2>nul

REM Copy source files
echo 📋 Copying source files...
copy "android\MainActivity.java" "android_project\app\src\main\java\com\zeevweinerich\honeynet\" >nul
copy "android\AndroidManifest.xml" "android_project\app\src\main\" >nul
copy "android\activity_main.xml" "android_project\app\src\main\res\layout\" >nul
copy "android\build.gradle" "android_project\app\" >nul

REM Create strings.xml
echo 📝 Creating resources...
echo ^<?xml version="1.0" encoding="utf-8"?^> > android_project\app\src\main\res\values\strings.xml
echo ^<resources^> >> android_project\app\src\main\res\values\strings.xml
echo     ^<string name="app_name"^>HoneyNet^</string^> >> android_project\app\src\main\res\values\strings.xml
echo     ^<string name="loading"^>Loading HoneyNet...^</string^> >> android_project\app\src\main\res\values\strings.xml
echo ^</resources^> >> android_project\app\src\main\res\values\strings.xml

REM Create colors.xml
echo ^<?xml version="1.0" encoding="utf-8"?^> > android_project\app\src\main\res\values\colors.xml
echo ^<resources^> >> android_project\app\src\main\res\values\colors.xml
echo     ^<color name="primary"^>#2c3e50^</color^> >> android_project\app\src\main\res\values\colors.xml
echo     ^<color name="primary_dark"^>#1a252f^</color^> >> android_project\app\src\main\res\values\colors.xml
echo     ^<color name="accent"^>#e74c3c^</color^> >> android_project\app\src\main\res\values\colors.xml
echo ^</resources^> >> android_project\app\src\main\res\values\colors.xml

REM Create root build.gradle
echo 📦 Creating build configuration...
echo buildscript { > android_project\build.gradle
echo     repositories { >> android_project\build.gradle
echo         google() >> android_project\build.gradle
echo         mavenCentral() >> android_project\build.gradle
echo     } >> android_project\build.gradle
echo     dependencies { >> android_project\build.gradle
echo         classpath 'com.android.tools.build:gradle:8.0.2' >> android_project\build.gradle
echo     } >> android_project\build.gradle
echo } >> android_project\build.gradle

REM Create gradle.properties
echo android.useAndroidX=true > android_project\gradle.properties
echo android.enableJetifier=true >> android_project\gradle.properties

echo.
echo 🔨 Building APK...
cd android_project

REM Initialize Gradle wrapper
if not exist "gradlew.bat" (
    echo 📥 Downloading Gradle wrapper...
    gradle wrapper --gradle-version 8.0
)

REM Build APK
echo 🚀 Compiling and building APK...
call gradlew.bat assembleRelease

if exist "app\build\outputs\apk\release\app-release.apk" (
    echo.
    echo ✅ SUCCESS! APK built successfully!
    echo.
    echo 📱 APK Location: app\build\outputs\apk\release\app-release.apk
    echo 📏 APK Size: 
    dir "app\build\outputs\apk\release\app-release.apk" | find "app-release.apk"
    echo.
    echo 🚀 Ready for installation on Android devices!
    echo.
    
    REM Copy to distribution folder
    copy "app\build\outputs\apk\release\app-release.apk" "..\HoneyNet-Android.apk" >nul
    echo 📦 APK copied to: HoneyNet-Android.apk
    
) else (
    echo.
    echo ❌ Build failed! Check the error messages above.
    echo.
    echo 💡 Alternative APK creation methods:
    echo.
    echo 1. Online APK Builder:
    echo    - Go to: https://appsgeyser.com/
    echo    - Choose "Website to App"
    echo    - URL: http://18.209.27.121
    echo    - App Name: HoneyNet
    echo.
    echo 2. MIT App Inventor:
    echo    - Go to: https://appinventor.mit.edu/
    echo    - Create WebViewer app
    echo    - Set URL to HoneyNet platform
    echo.
    echo 3. PhoneGap Build:
    echo    - Go to: https://build.phonegap.com/
    echo    - Upload source code
    echo    - Build APK online
)

cd ..

:end
echo.
echo ========================================
echo   Build process completed!
echo ========================================
pause
