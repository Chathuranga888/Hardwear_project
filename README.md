# Smart Charging Locker System

A secure IoT-based charging station system built with Raspberry Pi Zero that provides fingerprint-authenticated phone charging lockers with real-time monitoring and Firebase integration.

## 🚀 Project Overview

This project implements a smart charging locker system that allows users to securely charge their phones in individual lockers. The system uses biometric fingerprint authentication for access control and provides real-time monitoring through a web interface. Built specifically for Raspberry Pi Zero, it combines hardware control with cloud connectivity for a complete IoT solution.

## ✨ Features

- **Biometric Security**: Fingerprint enrollment and authentication using pyfingerprint
- **Multiple Charging Lockers**: Support for 4 individual charging compartments with solenoid locks
- **Real-time Monitoring**: Live image capture and Firebase cloud storage
- **User-friendly GUI**: PySimpleGUI-based interface for easy interaction
- **Firebase Integration**: Real-time database and cloud storage for data management
- **IR Sensors**: Detection of phone presence in charging compartments
- **Pi Camera Support**: Image capture for security and monitoring
- **Notification System**: Real-time alerts and status updates

## 🛠️ Hardware Requirements

### Main Components
- **Raspberry Pi Zero W** - Main controller board
- **Fingerprint Sensor** - Biometric authentication (connected via UART)
- **Pi Camera Module** - Image capture and monitoring
- **4x Solenoid Locks** - Secure locker mechanisms
- **4x IR Sensors** - Phone detection in compartments
- **GPIO Expansion** - For multiple device connections

### GPIO Pin Configuration
```
Solenoid Locks: GPIO pins 17, 27, 22, 23
IR Sensors: GPIO pins 6, 13, 19, 26
Fingerprint Sensor: UART (/dev/ttyS0)
```

## 💻 Software Dependencies

### Python Libraries
```bash
# Core GUI Framework
PySimpleGUI

# Hardware Interface
RPi.GPIO
picamera
pyfingerprint

# Firebase Integration
firebase-admin

# Additional Libraries
time
threading
requests
flask
os
random
```

### Firebase Setup
- Firebase Realtime Database
- Firebase Storage
- Firebase Admin SDK

## 📁 Project Structure

```
Hardwear_project/
├── gui_v2.py                    # Main GUI application
├── gui_w_v2.py                  # Windows-compatible GUI version
├── newGUI1.3.py                 # Latest GUI implementation
├── oldGUI.py                    # Legacy GUI version
├── insert_data_to_firebase_new.py    # Firebase data insertion
├── send_real_time_image_new.py       # Real-time image upload
├── delete_data_from_firebase_new.py  # Firebase data management
├── new_v1.py / new_w_v1.py           # Core functionality modules
├── hardware-project-*.json           # Firebase service account key
├── images.png                         # System images
├── photo_1.jpg                        # Sample photo
└── image/                             # UI images directory
    ├── enrollf_error_image.png
    ├── eadingf_image.png
    ├── safe_charging_img.png
    ├── phone_charge_complete.png
    └── ... (other UI images)
```

## 🔧 Installation & Setup

### 1. Hardware Setup
```bash
# Enable UART for fingerprint sensor
sudo raspi-config
# Navigate to Interface Options > Serial Port
# Enable serial port hardware, disable serial console

# Enable Camera
sudo raspi-config
# Navigate to Interface Options > Camera > Enable
```

### 2. Software Installation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python dependencies
pip install PySimpleGUI
pip install RPi.GPIO
pip install picamera
pip install pyfingerprint
pip install firebase-admin
pip install requests
pip install flask

# Clone and setup project
git clone [repository-url]
cd Hardwear_project
```

### 3. Firebase Configuration
1. Create a Firebase project at https://console.firebase.google.com
2. Generate a service account key (JSON file)
3. Replace `hardware-project-*.json` with your service account key
4. Update Firebase URLs in the Python files:
   ```python
   'databaseURL': 'your-database-url'
   'storageBucket': 'your-storage-bucket'
   ```

### 4. GPIO Setup
```bash
# Test GPIO functionality
python -c "import RPi.GPIO as GPIO; print('GPIO library working')"

# Verify camera
raspistill -o test_image.jpg
```

## 🚀 Usage

### Running the Main Application
```bash
# Start the main GUI application
python gui_v2.py

# For development/testing on Windows
python gui_w_v2.py
```

### System Operations

1. **User Registration**
   - Place finger on sensor
   - System enrolls fingerprint
   - Assigns unique user ID

2. **Charging Process**
   - Authenticate with fingerprint
   - Select available locker
   - Place phone and close locker
   - System locks compartment

3. **Retrieval Process**
   - Authenticate with fingerprint
   - System unlocks assigned locker
   - Retrieve phone
   - System resets locker status

### Firebase Operations
```bash
# Upload images to Firebase Storage
python send_real_time_image_new.py

# Insert user data
python insert_data_to_firebase_new.py

# Delete user data
python delete_data_from_firebase_new.py
```

## 🔌 API Endpoints

The system includes Flask-based API endpoints for remote monitoring:

- `/status` - Get system status
- `/unlock/<locker_id>` - Remote unlock functionality
- `/users` - Manage user database

## 📊 Monitoring & Analytics

- **Real-time Database**: User authentication logs
- **Cloud Storage**: Security images and system photos
- **Status Monitoring**: Locker occupancy and charging status
- **Notification System**: User alerts and system messages

## 🛡️ Security Features

- **Biometric Authentication**: Secure fingerprint-based access
- **Image Logging**: Photo capture for security monitoring
- **Encrypted Communication**: Secure Firebase connection
- **Access Control**: User-specific locker assignments

## 🔧 Troubleshooting

### Common Issues

1. **Fingerprint Sensor Not Detected**
   ```bash
   # Check UART connection
   ls -la /dev/ttyS0
   sudo chmod 666 /dev/ttyS0
   ```

2. **Camera Module Issues**
   ```bash
   # Verify camera connection
   vcgencmd get_camera
   # Should return: supported=1 detected=1
   ```

3. **GPIO Permission Errors**
   ```bash
   # Add user to gpio group
   sudo usermod -a -G gpio $USER
   # Logout and login again
   ```

4. **Firebase Connection Issues**
   - Verify internet connection
   - Check service account key file
   - Validate Firebase project configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Hardware Team** - Raspberry Pi integration and sensor setup
- **Software Team** - GUI development and Firebase integration
- **Security Team** - Biometric authentication implementation

## 🙏 Acknowledgments

- Raspberry Pi Foundation for excellent documentation
- Firebase team for cloud services
- PySimpleGUI community for UI framework
- pyfingerprint library contributors

## 📞 Support

For technical support or questions:
- Create an issue in the GitHub repository
- Check troubleshooting section above
- Review Firebase console for cloud-related issues

---

**Note**: This project is designed specifically for Raspberry Pi Zero W. Some features may require adaptation for other hardware platforms.