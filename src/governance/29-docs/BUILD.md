# Build Guide

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (optional)
- Make

## Build from Source

### 1. Clone Repository

```bash
git clone https://github.com/SynergyMesh-admin/SynergyMesh.git
cd SynergyMesh/governance
```

### 2. Install Dependencies

```bash
make install
```

### 3. Run Tests

```bash
make test
```

### 4. Build Package

```bash
make build
```

## Platform-Specific Builds

### Windows

```bash
cd build/windows
./build-windows.bat
```

### macOS

```bash
cd build/macos
./build-macos.sh
```

### Linux

```bash
cd build/linux
./build-linux.sh
```

## Docker Build

```bash
docker-compose build
```

---

**Last Updated**: 2025-12-10
