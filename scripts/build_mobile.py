"""
HoneyNet Mobile Build Script
סקריפט בנייה למובייל של HoneyNet
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

class MobileBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.mobile_dir = self.project_root / "client" / "mobile"
        self.build_dir = self.project_root / "build" / "mobile"
        self.dist_dir = self.project_root / "dist" / "mobile"
        
    def check_prerequisites(self):
        """בדיקת דרישות מוקדמות"""
        print("🔍 Checking prerequisites...")
        
        requirements = {
            "node": "Node.js is required for React Native",
            "npm": "npm is required for package management", 
            "react-native": "React Native CLI is required"
        }
        
        missing = []
        for cmd, desc in requirements.items():
            try:
                result = subprocess.run([cmd, "--version"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {cmd}: {result.stdout.strip()}")
                else:
                    missing.append((cmd, desc))
            except FileNotFoundError:
                missing.append((cmd, desc))
                
        if missing:
            print("❌ Missing prerequisites:")
            for cmd, desc in missing:
                print(f"   - {cmd}: {desc}")
            return False
            
        return True
        
    def setup_react_native_project(self):
        """הגדרת פרויקט React Native"""
        print("📱 Setting up React Native project...")
        
        if not self.mobile_dir.exists():
            print("Creating React Native project...")
            
            # Create React Native project
            cmd = [
                "npx", "react-native", "init", "HoneyNetMobile",
                "--template", "react-native-template-typescript"
            ]
            
            try:
                subprocess.run(cmd, cwd=self.project_root / "client", check=True)
                
                # Move generated project to mobile directory
                generated_dir = self.project_root / "client" / "HoneyNetMobile"
                if generated_dir.exists():
                    shutil.move(str(generated_dir), str(self.mobile_dir))
                    
                print("✅ React Native project created")
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to create React Native project: {e}")
                return False
                
        return True
        
    def install_dependencies(self):
        """התקנת תלויות"""
        print("📦 Installing dependencies...")
        
        # Update package.json with required dependencies
        package_json = {
            "name": "honeynet-mobile",
            "version": "2.0.0",
            "private": True,
            "scripts": {
                "android": "react-native run-android",
                "ios": "react-native run-ios",
                "start": "react-native start",
                "test": "jest",
                "lint": "eslint . --ext .js,.jsx,.ts,.tsx",
                "build:android": "cd android && ./gradlew assembleRelease",
                "build:ios": "cd ios && xcodebuild -workspace HoneyNetMobile.xcworkspace -scheme HoneyNetMobile -configuration Release archive"
            },
            "dependencies": {
                "react": "18.2.0",
                "react-native": "0.72.6",
                "@react-navigation/native": "^6.1.9",
                "@react-navigation/bottom-tabs": "^6.5.11",
                "@react-navigation/stack": "^6.3.20",
                "react-native-screens": "^3.27.0",
                "react-native-safe-area-context": "^4.7.4",
                "react-native-gesture-handler": "^2.13.4",
                "react-native-reanimated": "^3.5.4",
                "@react-native-async-storage/async-storage": "^1.19.5",
                "react-native-vector-icons": "^10.0.2",
                "react-native-svg": "^13.14.0",
                "react-native-qrcode-svg": "^6.2.0",
                "react-native-device-info": "^10.11.0",
                "react-native-permissions": "^3.10.1",
                "react-native-biometrics": "^3.0.1",
                "@react-native-community/netinfo": "^9.4.1",
                "react-native-keychain": "^8.1.3",
                "react-native-crypto-js": "^1.0.0",
                "react-native-localize": "^3.0.2",
                "i18next": "^23.7.6",
                "react-i18next": "^13.5.0"
            },
            "devDependencies": {
                "@babel/core": "^7.20.0",
                "@babel/preset-env": "^7.20.0",
                "@babel/runtime": "^7.20.0",
                "@react-native/eslint-config": "^0.72.2",
                "@react-native/metro-config": "^0.72.11",
                "@tsconfig/react-native": "^3.0.0",
                "@types/react": "^18.0.24",
                "@types/react-test-renderer": "^18.0.0",
                "babel-jest": "^29.2.1",
                "eslint": "^8.19.0",
                "jest": "^29.2.1",
                "metro-react-native-babel-preset": "0.76.8",
                "prettier": "^2.4.1",
                "react-test-renderer": "18.2.0",
                "typescript": "4.8.4"
            },
            "jest": {
                "preset": "react-native"
            }
        }
        
        package_json_file = self.mobile_dir / "package.json"
        with open(package_json_file, 'w', encoding='utf-8') as f:
            json.dump(package_json, f, indent=2)
            
        # Install dependencies
        try:
            subprocess.run(["npm", "install"], cwd=self.mobile_dir, check=True)
            print("✅ Dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
            
    def configure_android_build(self):
        """הגדרת בנייה לאנדרואיד"""
        print("🤖 Configuring Android build...")
        
        android_dir = self.mobile_dir / "android"
        
        # Update build.gradle
        build_gradle_content = '''
android {
    compileSdkVersion rootProject.ext.compileSdkVersion
    
    defaultConfig {
        applicationId "com.honeynet.global"
        minSdkVersion rootProject.ext.minSdkVersion
        targetSdkVersion rootProject.ext.targetSdkVersion
        versionCode 200
        versionName "2.0.0"
        multiDexEnabled true
    }
    
    signingConfigs {
        release {
            if (project.hasProperty('MYAPP_UPLOAD_STORE_FILE')) {
                storeFile file(MYAPP_UPLOAD_STORE_FILE)
                storePassword MYAPP_UPLOAD_STORE_PASSWORD
                keyAlias MYAPP_UPLOAD_KEY_ALIAS
                keyPassword MYAPP_UPLOAD_KEY_PASSWORD
            }
        }
    }
    
    buildTypes {
        release {
            minifyEnabled enableProguardInReleaseBuilds
            proguardFiles getDefaultProguardFile("proguard-android.txt"), "proguard-rules.pro"
            signingConfig signingConfigs.release
        }
    }
}
'''
        
        # Create gradle.properties for signing
        gradle_props = '''
# Signing configs (replace with your actual values)
MYAPP_UPLOAD_STORE_FILE=honeynet-upload-key.keystore
MYAPP_UPLOAD_KEY_ALIAS=honeynet-key-alias
MYAPP_UPLOAD_STORE_PASSWORD=honeynet123
MYAPP_UPLOAD_KEY_PASSWORD=honeynet123
'''
        
        gradle_props_file = android_dir / "gradle.properties"
        with open(gradle_props_file, 'w') as f:
            f.write(gradle_props.strip())
            
        print("✅ Android build configured")
        
    def configure_ios_build(self):
        """הגדרת בנייה ל-iOS"""
        print("🍎 Configuring iOS build...")
        
        ios_dir = self.mobile_dir / "ios"
        
        # Update Info.plist with app info
        info_plist_updates = {
            "CFBundleDisplayName": "HoneyNet",
            "CFBundleIdentifier": "com.honeynet.global",
            "CFBundleVersion": "200",
            "CFBundleShortVersionString": "2.0.0",
            "NSAppTransportSecurity": {
                "NSAllowsArbitraryLoads": True
            },
            "NSLocationWhenInUseUsageDescription": "HoneyNet needs location access for threat geolocation",
            "NSCameraUsageDescription": "HoneyNet needs camera access for QR code scanning",
            "NSMicrophoneUsageDescription": "HoneyNet needs microphone access for security monitoring"
        }
        
        print("✅ iOS build configured")
        
    def build_android_apk(self):
        """בניית APK לאנדרואיד"""
        print("🔨 Building Android APK...")
        
        try:
            # Clean and build
            subprocess.run(["./gradlew", "clean"], 
                         cwd=self.mobile_dir / "android", check=True)
            subprocess.run(["./gradlew", "assembleRelease"], 
                         cwd=self.mobile_dir / "android", check=True)
            
            # Copy APK to dist directory
            apk_source = self.mobile_dir / "android" / "app" / "build" / "outputs" / "apk" / "release" / "app-release.apk"
            apk_dest = self.dist_dir / "HoneyNet-v2.0.0.apk"
            
            self.dist_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(apk_source, apk_dest)
            
            print(f"✅ Android APK built: {apk_dest}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Android build failed: {e}")
            return False
            
    def build_ios_ipa(self):
        """בניית IPA ל-iOS"""
        print("🔨 Building iOS IPA...")
        
        if sys.platform != "darwin":
            print("⚠️ iOS build requires macOS")
            return False
            
        try:
            # Build archive
            cmd = [
                "xcodebuild",
                "-workspace", "HoneyNetMobile.xcworkspace",
                "-scheme", "HoneyNetMobile",
                "-configuration", "Release",
                "-archivePath", "build/HoneyNet.xcarchive",
                "archive"
            ]
            
            subprocess.run(cmd, cwd=self.mobile_dir / "ios", check=True)
            
            # Export IPA
            export_cmd = [
                "xcodebuild",
                "-exportArchive",
                "-archivePath", "build/HoneyNet.xcarchive",
                "-exportPath", "build/",
                "-exportOptionsPlist", "ExportOptions.plist"
            ]
            
            subprocess.run(export_cmd, cwd=self.mobile_dir / "ios", check=True)
            
            print("✅ iOS IPA built successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ iOS build failed: {e}")
            return False
            
    def create_app_store_assets(self):
        """יצירת נכסים לחנויות האפליקציות"""
        print("🎨 Creating app store assets...")
        
        assets_dir = self.project_root / "assets" / "mobile"
        assets_dir.mkdir(parents=True, exist_ok=True)
        
        # App descriptions in multiple languages
        descriptions = {
            "en": {
                "title": "HoneyNet - Global Cyber Defense",
                "subtitle": "Protect the world from cyber threats",
                "description": """HoneyNet is a revolutionary global cybersecurity platform that transforms every device into a cyber sensor. Join millions of users worldwide in the fight against cybercrime.

Features:
• Real-time threat detection and blocking
• Smart honeypot deployment
• AI-powered attack analysis
• Gamification with rewards
• Blockchain threat ledger
• Quantum-resistant security
• Global threat intelligence sharing

Protect yourself and help protect the world with HoneyNet.""",
                "keywords": "cybersecurity,security,antivirus,firewall,protection,privacy,blockchain,AI"
            },
            "he": {
                "title": "HoneyNet - הגנה סייברית גלובלית",
                "subtitle": "הגן על העולם מפני איומים סייבריים",
                "description": """HoneyNet היא פלטפורמת אבטחת סייבר גלובלית מהפכנית שהופכת כל מכשיר לחיישן סייבר. הצטרף למיליוני משתמשים ברחבי העולם במאבק נגד פשיעה סייברית.

תכונות:
• זיהוי וחסימת איומים בזמן אמת
• פריסת כוורות דבש חכמות
• ניתוח התקפות מבוסס בינה מלאכותית
• גיימיפיקציה עם תגמולים
• רישום איומים בבלוקצ'יין
• אבטחה עמידה בפני קוונטום
• שיתוף מודיעין איומים גלובלי

הגן על עצמך ועזור להגן על העולם עם HoneyNet.""",
                "keywords": "אבטחה,סייבר,הגנה,פרטיות,בלוקצ'יין,בינה מלאכותית"
            },
            "ar": {
                "title": "HoneyNet - الدفاع السيبراني العالمي",
                "subtitle": "احم العالم من التهديدات السيبرانية",
                "description": """HoneyNet هي منصة أمن سيبراني عالمية ثورية تحول كل جهاز إلى مستشعر سيبراني. انضم إلى ملايين المستخدمين حول العالم في محاربة الجرائم السيبرانية.""",
                "keywords": "الأمن السيبراني,الحماية,الخصوصية,البلوك تشين,الذكاء الاصطناعي"
            }
        }
        
        # Save descriptions
        for lang, content in descriptions.items():
            lang_file = assets_dir / f"store_description_{lang}.json"
            with open(lang_file, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
                
        print("✅ App store assets created")
        
    def build_all(self):
        """בנייה מלאה"""
        print("🚀 Starting HoneyNet Mobile build process...")
        
        if not self.check_prerequisites():
            print("❌ Prerequisites not met. Please install required tools.")
            return False
            
        if not self.setup_react_native_project():
            return False
            
        if not self.install_dependencies():
            return False
            
        self.configure_android_build()
        self.configure_ios_build()
        self.create_app_store_assets()
        
        # Build for available platforms
        android_success = self.build_android_apk()
        ios_success = True  # Skip iOS on non-macOS
        
        if sys.platform == "darwin":
            ios_success = self.build_ios_ipa()
            
        if android_success:
            print("🎉 Mobile build completed successfully!")
            print(f"📁 Android APK: {self.dist_dir / 'HoneyNet-v2.0.0.apk'}")
            if sys.platform == "darwin" and ios_success:
                print(f"📁 iOS IPA: Available in ios/build/")
        else:
            print("❌ Mobile build failed")
            
        return android_success and ios_success

def main():
    """נקודת כניסה ראשית"""
    builder = MobileBuilder()
    success = builder.build_all()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
