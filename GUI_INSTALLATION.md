# 🖥️ GUI Installation Guide

This guide provides detailed instructions for installing and setting up the Make It Heavy GUI on different operating systems.

## 📋 System Requirements

### Minimum Requirements
- **OS**: macOS 10.14+, Windows 10+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB free space
- **Display**: 1024x768 minimum resolution

### Recommended Requirements
- **OS**: macOS 12+, Windows 11, or Linux (Ubuntu 20.04+)
- **Python**: 3.9 or higher
- **RAM**: 8GB or more
- **Storage**: 1GB free space
- **Display**: 1920x1080 or higher resolution

## 🍎 macOS Installation

### Step 1: Install Python and Dependencies

**Using Homebrew (Recommended):**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and tkinter
brew install python python-tk

# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Using Python.org installer:**
1. Download Python from [python.org](https://www.python.org/downloads/macos/)
2. Install Python (tkinter is included by default)
3. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Step 2: Clone and Setup Project

```bash
# Clone the repository
git clone https://github.com/Kylo111/make-it-heavy.git
cd make-it-heavy

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### Step 3: Install GUI-Specific Dependencies

```bash
# Install additional GUI dependencies
uv pip install pillow matplotlib pandas numpy

# Verify tkinter installation
python -c "import tkinter; print('Tkinter is available')"
```

### Step 4: Launch GUI

```bash
# Launch the GUI
python gui/main_app.py

# Or with debug mode
python gui/main_app.py --debug
```

### macOS-Specific Notes

- **Dark Mode**: GUI automatically detects macOS dark mode
- **Retina Displays**: GUI scales automatically for high-DPI displays
- **Keyboard Shortcuts**: Uses Cmd key instead of Ctrl
- **Menu Integration**: Native macOS menu bar integration

## 🪟 Windows Installation

### Step 1: Install Python

**Using Microsoft Store (Recommended):**
1. Open Microsoft Store
2. Search for "Python 3.11" or newer
3. Install Python (tkinter included by default)

**Using Python.org installer:**
1. Download Python from [python.org](https://www.python.org/downloads/windows/)
2. Run installer and check "Add Python to PATH"
3. Ensure "tcl/tk and IDLE" is selected during installation

### Step 2: Install uv Package Manager

```cmd
# Using pip
pip install uv

# Or using PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Step 3: Clone and Setup Project

```cmd
# Clone the repository
git clone https://github.com/Kylo111/make-it-heavy.git
cd make-it-heavy

# Create virtual environment
uv venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

### Step 4: Install GUI Dependencies

```cmd
# Install GUI-specific dependencies
uv pip install pillow matplotlib pandas numpy

# Verify tkinter installation
python -c "import tkinter; print('Tkinter is available')"
```

### Step 5: Launch GUI

```cmd
# Launch the GUI
python gui/main_app.py

# Or with debug mode
python gui/main_app.py --debug
```

### Windows-Specific Notes

- **Windows Theme**: GUI follows Windows 10/11 theme settings
- **High DPI**: Automatic scaling for high-DPI displays
- **Keyboard Shortcuts**: Uses Ctrl key combinations
- **File Associations**: Can associate .heavy files with the GUI

### Windows Troubleshooting

**Common Issues:**

**Python not found:**
```cmd
# Add Python to PATH manually
set PATH=%PATH%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311
```

**tkinter not available:**
```cmd
# Reinstall Python with tkinter
# Download from python.org and ensure "tcl/tk and IDLE" is checked
```

**Permission errors:**
```cmd
# Run as administrator or use --user flag
pip install --user -r requirements.txt
```

## 🐧 Linux Installation

### Ubuntu/Debian

**Step 1: Install System Dependencies**
```bash
# Update package list
sudo apt update

# Install Python and tkinter
sudo apt install python3 python3-pip python3-tk python3-venv

# Install additional GUI dependencies
sudo apt install python3-pil python3-pil.imagetk

# Install development tools
sudo apt install build-essential python3-dev
```

**Step 2: Install uv Package Manager**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Step 3: Setup Project**
```bash
# Clone repository
git clone https://github.com/Kylo111/make-it-heavy.git
cd make-it-heavy

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

**Step 4: Launch GUI**
```bash
# Launch GUI
python gui/main_app.py

# Or with debug mode
python gui/main_app.py --debug
```

### Fedora/CentOS/RHEL

**Step 1: Install System Dependencies**
```bash
# Fedora
sudo dnf install python3 python3-pip python3-tkinter python3-pillow

# CentOS/RHEL (with EPEL)
sudo yum install epel-release
sudo yum install python3 python3-pip tkinter python3-pillow
```

**Step 2: Continue with uv installation and project setup as above**

### Arch Linux

**Step 1: Install Dependencies**
```bash
# Install Python and tkinter
sudo pacman -S python python-pip tk python-pillow

# Install development tools
sudo pacman -S base-devel
```

**Step 2: Continue with uv installation and project setup as above**

### Linux-Specific Notes

- **Desktop Environment**: GUI adapts to GNOME, KDE, XFCE themes
- **Wayland Support**: Full Wayland compatibility
- **X11 Support**: Traditional X11 support
- **Font Rendering**: Uses system font rendering

## 🔧 Advanced Installation Options

### Development Installation

For developers who want to contribute or modify the GUI:

```bash
# Clone with development dependencies
git clone https://github.com/Kylo111/make-it-heavy.git
cd make-it-heavy

# Create development environment
uv venv --python 3.9
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install with development dependencies
uv pip install -r requirements.txt
uv pip install pytest black flake8 mypy

# Install in editable mode
uv pip install -e .
```

### Docker Installation

For containerized deployment:

```bash
# Build Docker image
docker build -t make-it-heavy-gui .

# Run with X11 forwarding (Linux)
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $(pwd)/config.yaml:/app/config.yaml \
  make-it-heavy-gui

# Run with VNC (cross-platform)
docker run -it --rm \
  -p 5901:5901 \
  -v $(pwd)/config.yaml:/app/config.yaml \
  make-it-heavy-gui-vnc
```

### Portable Installation

Create a portable version that doesn't require system installation:

```bash
# Create portable directory
mkdir make-it-heavy-portable
cd make-it-heavy-portable

# Download portable Python (Windows)
# Download from https://www.python.org/downloads/windows/
# Extract to python/ directory

# Clone project
git clone https://github.com/Kylo111/make-it-heavy.git app

# Create launcher script
cat > launch.bat << 'EOF'
@echo off
cd app
..\python\python.exe gui\main_app.py
EOF

# Make executable (Linux/macOS)
cat > launch.sh << 'EOF'
#!/bin/bash
cd app
../python/bin/python gui/main_app.py
EOF
chmod +x launch.sh
```

## 🧪 Testing Installation

### Verification Script

Create a test script to verify your installation:

```python
# test_installation.py
import sys
import importlib

def test_module(module_name):
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name} - OK")
        return True
    except ImportError as e:
        print(f"❌ {module_name} - FAILED: {e}")
        return False

def main():
    print("Testing Make It Heavy GUI Installation")
    print("=" * 40)
    
    required_modules = [
        'tkinter',
        'PIL',
        'matplotlib',
        'pandas',
        'numpy',
        'openai',
        'yaml',
        'requests'
    ]
    
    all_good = True
    for module in required_modules:
        if not test_module(module):
            all_good = False
    
    print("=" * 40)
    if all_good:
        print("🎉 All dependencies installed successfully!")
        print("You can now run: python gui/main_app.py")
    else:
        print("❌ Some dependencies are missing. Please install them.")
        print("Run: uv pip install -r requirements.txt")

if __name__ == "__main__":
    main()
```

Run the test:
```bash
python test_installation.py
```

### GUI Test

Test the GUI specifically:

```bash
# Quick GUI test
python -c "
import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt

root = tk.Tk()
root.title('GUI Test')
label = tk.Label(root, text='GUI components working!')
label.pack()
root.after(2000, root.destroy)
root.mainloop()
print('GUI test completed successfully!')
"
```

## 🚨 Troubleshooting

### Common Installation Issues

**Python Version Issues:**
```bash
# Check Python version
python --version
python3 --version

# Use specific Python version
python3.9 -m venv .venv
```

**Permission Issues:**
```bash
# Linux/macOS: Use user installation
pip install --user -r requirements.txt

# Windows: Run as administrator or use --user
```

**tkinter Missing:**
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# macOS with Homebrew
brew install python-tk

# Windows: Reinstall Python with tkinter
```

**Display Issues (Linux):**
```bash
# X11 forwarding for SSH
ssh -X username@hostname

# Wayland compatibility
export GDK_BACKEND=x11
```

### Platform-Specific Issues

**macOS:**
- **Gatekeeper**: Right-click and "Open" if blocked
- **Permissions**: Grant accessibility permissions if needed
- **Homebrew**: Update Homebrew if packages fail to install

**Windows:**
- **Antivirus**: Add Python to antivirus exceptions
- **Windows Defender**: Allow Python through firewall
- **Path Issues**: Ensure Python is in system PATH

**Linux:**
- **Display Server**: Ensure X11 or Wayland is running
- **Permissions**: Check file permissions in project directory
- **Dependencies**: Install distribution-specific packages

### Getting Help

If you encounter issues:

1. **Check System Requirements**: Ensure your system meets minimum requirements
2. **Update Dependencies**: Run `uv pip install --upgrade -r requirements.txt`
3. **Check Logs**: Look for error messages in terminal output
4. **Test Components**: Use the verification script above
5. **Seek Help**: Create an issue on GitHub with:
   - Operating system and version
   - Python version
   - Error messages
   - Steps to reproduce

## 📚 Next Steps

After successful installation:

1. **Configure API Keys**: Set up your OpenRouter or DeepSeek API keys
2. **Read User Guide**: Check out `GUI_USER_GUIDE.md` for detailed usage instructions
3. **Try Examples**: Start with simple queries to test functionality
4. **Explore Features**: Try multi-agent mode and advanced features
5. **Join Community**: Connect with other users for tips and support

---

**Installation complete!** 🎉

You're now ready to use the Make It Heavy GUI. Launch it with:
```bash
python gui/main_app.py
```

For detailed usage instructions, see the [GUI User Guide](GUI_USER_GUIDE.md).