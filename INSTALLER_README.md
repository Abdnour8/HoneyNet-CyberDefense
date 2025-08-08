# HoneyNet Professional Installer v3.0

## Overview
This is the official professional installer for HoneyNet - Global Cyber Defense Platform. The installer provides a complete, user-friendly installation experience with an English interface and comprehensive system setup.

## Features
- **Professional GUI Interface** - Modern, intuitive installation wizard
- **Component Selection** - Choose which components to install
- **System Requirements Check** - Automatic validation of system compatibility
- **Dependency Management** - Automatic installation of Python packages
- **Service Configuration** - Windows service setup with auto-start
- **Database Setup** - Automatic database initialization
- **Shortcut Creation** - Desktop and Start Menu shortcuts
- **Installation Logging** - Detailed logs for troubleshooting

## Installation Methods

### Method 1: Batch File (Recommended)
1. Right-click `install_honeynet.bat`
2. Select "Run as administrator"
3. Follow the on-screen instructions

### Method 2: Python Script
1. Open Command Prompt as Administrator
2. Navigate to the installer directory
3. Run: `python HoneyNet_Professional_Installer.py`

## System Requirements
- **Operating System**: Windows 10/11 (64-bit)
- **Memory**: 8GB RAM minimum (16GB recommended)
- **Storage**: 10GB free disk space
- **Python**: Version 3.8 or higher
- **Privileges**: Administrator rights required
- **Network**: Internet connection for dependency downloads

## Components Installed

### Core Components
- **Defense Engine** - Main threat detection and response system
- **Threat Analyzer** - AI-powered threat analysis with machine learning
- **Swarm Intelligence** - Collective defense coordination
- **Quantum Honeypots** - Advanced decoy systems

### Server Components
- **FastAPI Server** - RESTful API and web interface
- **WebSocket Handler** - Real-time communication
- **Global Analytics** - Threat intelligence processing
- **Database Layer** - PostgreSQL/SQLite data storage

### Client Applications
- **Desktop Client** - Windows management interface
- **Web Interface** - Browser-based control panel
- **Mobile Support** - Android/iOS connectivity

### Advanced Features
- **Blockchain Ledger** - Immutable threat records
- **Digital Twin** - System behavior modeling
- **Edge Computing** - Distributed processing
- **Gamification** - User engagement system

## Installation Process

### Step 1: Welcome & System Check
- Introduction to HoneyNet platform
- Automatic system requirements validation
- Compatibility verification

### Step 2: Component Selection
- Choose components to install
- View detailed descriptions
- Customize installation scope

### Step 3: Configuration
- Set installation directory
- Configure database options
- Setup Windows services
- Enable auto-start options

### Step 4: Installation
- Real-time progress monitoring
- Detailed installation logging
- Automatic dependency resolution
- Service registration

## Post-Installation

### Starting HoneyNet
After installation, you can start HoneyNet using:

1. **Desktop Shortcut** - Double-click the HoneyNet icon
2. **Start Menu** - Find HoneyNet in the Start Menu
3. **Command Line** - Run `python start_honeynet.py`
4. **Batch File** - Execute `start_honeynet.bat`

### Web Interface
Access the web interface at: `http://localhost:8000`

### Configuration Files
- Main config: `C:\HoneyNet\config\settings.py`
- User settings: `C:\HoneyNet\config\user_settings.json`
- Security config: `C:\HoneyNet\config\security.py`

### Logs
- Installation log: `installation.log`
- Runtime logs: `C:\HoneyNet\logs\`
- Service logs: Windows Event Viewer

## Troubleshooting

### Common Issues

#### Python Not Found
- Install Python 3.8+ from https://python.org
- Ensure Python is added to system PATH
- Restart Command Prompt after installation

#### Permission Denied
- Run installer as Administrator
- Check Windows UAC settings
- Verify user account has admin rights

#### Installation Fails
- Check installation.log for details
- Ensure sufficient disk space
- Verify internet connection for dependencies
- Temporarily disable antivirus software

#### Service Won't Start
- Check Windows Services console
- Verify Python path in service configuration
- Review service logs in Event Viewer

### Getting Help
- Check installation logs for error details
- Review system requirements
- Ensure all dependencies are installed
- Contact support with log files

## Uninstallation
To uninstall HoneyNet:
1. Stop all HoneyNet services
2. Remove from Windows Services
3. Delete installation directory
4. Remove shortcuts and registry entries

## Security Notes
- HoneyNet requires network access for threat intelligence
- Firewall exceptions may be needed for server components
- Database contains sensitive security information
- Regular backups of configuration recommended

## Version Information
- **Installer Version**: 3.0
- **HoneyNet Version**: Compatible with all v2.x releases
- **Build Date**: 2025-08-07
- **Python Compatibility**: 3.8+

## Support
For technical support and documentation:
- Installation logs: Check `installation.log`
- Runtime logs: `C:\HoneyNet\logs\`
- Configuration: Review settings files
- Community: HoneyNet user forums

---
**HoneyNet Professional Installer v3.0**  
*Global Cyber Defense Platform*  
*Professional Installation System*
