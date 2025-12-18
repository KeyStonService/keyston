# Uninstallation Guide

## Using pip

```bash
pip uninstall synergymesh-governance
```

## Platform-Specific Uninstallation

### Windows

1. Control Panel → Programs → Uninstall
2. Select "SynergyMesh Governance"
3. Click Uninstall

Or use uninstaller:

```bash
cd build/windows
./uninstall.bat
```

### macOS

```bash
cd build/macos
./uninstall-macos.sh
```

Or manually:

```bash
sudo rm -rf /Applications/SynergyMesh-Governance.app
rm -rf ~/Library/Application\ Support/SynergyMesh-Governance
```

### Linux

#### Debian/Ubuntu

```bash
sudo apt remove synergymesh-governance
```

#### Red Hat/CentOS

```bash
sudo rpm -e synergymesh-governance
```

## Clean User Data

```bash
rm -rf ~/.synergymesh-governance
```

---

**Last Updated**: 2025-12-10
