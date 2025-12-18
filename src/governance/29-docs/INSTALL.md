# Installation Guide

## Quick Install

### Using pip

```bash
pip install synergymesh-governance
```

### Using Docker

```bash
docker pull synergymesh/governance:latest
docker run -p 8080:8080 synergymesh/governance
```

## Platform-Specific Installation

### Windows

1. Download installer: `SynergyMesh-Governance-Setup.exe`
2. Run installer
3. Follow setup wizard

### macOS

1. Download DMG: `SynergyMesh-Governance.dmg`
2. Mount DMG
3. Drag to Applications

Or use Homebrew:

```bash
brew install synergymesh-governance
```

### Linux

#### Debian/Ubuntu

```bash
sudo dpkg -i synergymesh-governance_1.0.0_amd64.deb
```

#### Red Hat/CentOS

```bash
sudo rpm -i synergymesh-governance-1.0.0-1.x86_64.rpm
```

#### AppImage

```bash
chmod +x SynergyMesh-Governance-x86_64.AppImage
./SynergyMesh-Governance-x86_64.AppImage
```

## From Source

```bash
git clone https://github.com/SynergyMesh-admin/SynergyMesh.git
cd SynergyMesh/governance
make install
```

---

**Last Updated**: 2025-12-10
