# Deployment Guide

## Build Prerequisites

### Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Rust | 1.77+ | Backend compilation |
| Node.js | 18+ | Frontend build |
| Tauri CLI | 2.x | Bundle creation |
| cargo-tauri | 2.x | Build orchestration |

### Platform-Specific Requirements

**Windows**:
- Microsoft Visual Studio Build Tools (with C++ workload)
- WebView2 (included in Windows 10 1803+, Server 2022+; available as a download for older versions)
- WiX Toolset v3 or v4 (for `.msi` installer)

**macOS**:
- Xcode Command Line Tools
- For code signing: Apple Developer account + certificate

**Linux**:
- `libwebkit2gtk-4.1-dev`
- `libappindicator3-dev`
- `librsvg2-dev`
- `patchelf`
- `libssl-dev`

## Building for Production

### Standard Build

```bash
cd packages/desktopintel

# Full production build
npm run tauri:build

# Or run cargo directly for more control
cd src-tauri
cargo tauri build
```

### What the Build Does

1. **Frontend**: Runs `next build` to produce a static export
2. **Backend**: Runs `cargo build --release` to compile the Rust binary
3. **Bundle**: Tauri bundler packages the output into platform-specific installers
4. **Code signing**: If configured, binaries are signed (see below)

### Build Output

```
src-tauri/target/release/
├── jarvis-desktop-intelligence.exe   (Windows)
├── jarvis-desktop-intelligence       (Linux/macOS, debug)
└── bundle/
    ├── msi/   → *.msi  (Windows Installer)
    ├── dmg/   → *.dmg  (macOS Disk Image)
    └── appimage/  → *.AppImage  (Linux AppImage)
```

## Platform-Specific Builds

### Windows

```bash
# Build with MSI installer
npm run tauri:build

# Customize MSI in tauri.conf.json:
# "bundle": {
#   "windows": {
#     "wix": {
#       "language": "en-US",
#       "template": "main.wxs"
#     }
#   }
# }
```

### macOS

```bash
# Build for x86_64 (Intel)
npm run tauri:build

# Build for ARM64 (Apple Silicon)
# Set environment:
export CARGO_BUILD_TARGET=aarch64-apple-darwin
npm run tauri:build
```

### Linux

```bash
# Build with AppImage
npm run tauri:build

# Build with deb/rpm (requires additional config)
# See Tauri documentation for .deb and .rpm bundler config
```

## Code Signing

### Windows

1. Obtain an Authenticode certificate (from a CA or self-signed for testing)
2. Configure in `tauri.conf.json`:

```json
{
  "bundle": {
    "windows": {
      "sign": {
        "certificatePath": "./certs/my-cert.pfx",
        "password": "CERT_PASSWORD"
      }
    }
  }
}
```

Or sign manually after build:

```bash
signtool sign /fd SHA256 /a /f cert.pfx /p PASSWORD jarvis-desktop-intelligence.exe
```

### macOS

1. Obtain an Apple Developer ID Application certificate
2. Configure in `tauri.conf.json`:

```json
{
  "bundle": {
    "macOS": {
      "sign": {
        "identity": "Developer ID Application: Your Name (TEAMID)"
      }
    }
  }
}
```

Signing is applied automatically during `tauri build` when a valid identity is found in the keychain.

### Linux

AppImage supports GPG signing:

```bash
gpg --detach-sign --armor JARVIS_Desktop-1.0.0.AppImage
```

## Auto-Update Configuration

### Server Setup

The updater uses `tauri-plugin-updater`. Configure the update server URL in `tauri.conf.json`:

```json
{
  "plugins": {
    "updater": {
      "active": true,
      "endpoint": "https://updates.jarvis.ai/{{target}}/{{current_version}}",
      "dialog": true,
      "pubkey": "YOUR_UPDATER_PUBLIC_KEY"
    }
  }
}
```

### Update Manifest Format

The update endpoint must return a JSON response:

```json
{
  "version": "1.1.0",
  "notes": "Bug fixes and performance improvements",
  "pub_date": "2025-06-15T12:00:00Z",
  "platforms": {
    "windows-x86_64": {
      "signature": "...",
      "url": "https://releases.jarvis.ai/v1.1.0/jarvis-desktop-1.1.0.x64.msi"
    },
    "darwin-x86_64": {
      "signature": "...",
      "url": "https://releases.jarvis.ai/v1.1.0/jarvis-desktop-1.1.0.x64.dmg"
    },
    "darwin-aarch64": {
      "signature": "...",
      "url": "https://releases.jarvis.ai/v1.1.0/jarvis-desktop-1.1.0.aarch64.dmg"
    },
    "linux-x86_64": {
      "signature": "...",
      "url": "https://releases.jarvis.ai/v1.1.0/jarvis-desktop-1.1.0.x86_64.AppImage"
    }
  }
}
```

### Generating Signatures

```bash
# Generate key pair (one-time)
cargo tauri signer generate -w ~/.tauri/updater.key

# Sign a build
cargo tauri signer sign -k ~/.tauri/updater.key path/to/installer.msi
```

## Release Channels

The application supports three release channels:

| Channel | Config Value | Purpose | Auto-Update Enabled |
|---------|-------------|---------|---------------------|
| **Stable** | `stable` | Production releases | ✅ |
| **Beta** | `beta` | Pre-release testing | ✅ (opt-in) |
| **Nightly** | `nightly` | Daily development builds | ✅ (opt-in) |

Users configure their channel in **Settings → General → Update Channel**.

### Build per Channel

```bash
# For nightly builds, update tauri.conf.json version or use env vars:
export JARVIS_CHANNEL=nightly
npm run tauri:build
```

## Rollback Procedures

### Automatic Rollback

The `UpdateManager` supports rollback:

```rust
// If an update fails to apply:
update_manager.rollback();
// Resets update_available, latest_version, download_progress
```

### Manual Rollback

1. Uninstall the current version via OS package manager
2. Install the previous version from the releases archive
3. If auto-update re-applies the bad version, switch to the `stable` channel and temporarily disable auto-update

### Emergency Rollback

Distribution providers (winget, Homebrew, apt) can pin to a specific version using their respective pinning mechanisms.

## Distribution Options

| Method | Platform | Setup |
|--------|----------|-------|
| **Direct download** | All | Host MSI/DMG/AppImage on CDN or GitHub Releases |
| **winget** | Windows | Submit manifest to https://github.com/microsoft/winget-pkgs |
| **Homebrew Cask** | macOS | Submit formula to Homebrew Cask repository |
| **Snap Store** | Linux | Configure snapcraft.yaml and publish |
| **GitHub Releases** | All | Upload artifacts to GitHub Releases with release notes |
| **S3/CloudFront** | All | Host on private CDN with update manifest |

## Updates and Versioning

### Version Scheme

The project follows **Semantic Versioning**:

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: Breaking changes to IPC protocol, permission model, or data format
- **MINOR**: New features, new commands, new integration types
- **PATCH**: Bug fixes, performance improvements, security patches

### Version Declaration

The canonical version is in `src-tauri/Cargo.toml`:

```toml
[package]
name = "jarvis-desktop-intelligence"
version = "1.0.0"
```

The version is also reflected in `package.json` for the frontend.

### Update Flow

```
Application starts
    → UpdateManager checks for updates (if auto_check = true)
    → Update status shown in Dashboard
    → User triggers manual check (Command Palette or Updates page)
    → tauri-plugin-updater contacts update endpoint
    → If update available:
        → Download progress shown
        → User can apply or postpone
        → On apply: download → verify signature → install → restart
```

## Troubleshooting Deployment Issues

| Issue | Likely Cause | Solution |
|-------|-------------|----------|
| Build fails: "linker not found" | Missing C++ build tools | Install VS Build Tools (Windows) or Xcode CLT (macOS) |
| Build fails: "webkit2gtk not found" | Missing Linux dependencies | `sudo apt install libwebkit2gtk-4.1-dev` |
| MSI installer not created | WiX Toolset not installed | Install WiX v3 from https://wixtoolset.org |
| Code signing fails | Invalid or expired certificate | Renew certificate and update path/password in config |
| Auto-update not working | Incorrect endpoint URL or malformed manifest | Verify `endpoint` URL and JSON format match schema |
| App crashes on launch | WebView2 not available (Windows 7) | Install WebView2 evergreen runtime |
| DMG mount fails on macOS | Corrupted bundle | Rebuild and re-sign; verify `hardenedRuntime` in entitlements |
| AppImage fails to run on older Linux | FUSE version mismatch | Install fuse3 or use AppImageLauncher |
| Build too large | Unnecessary dependencies in release | Run `cargo bloat` to analyze; prune dependencies |
| Tauri CLI version mismatch | Global vs local version mismatch | Use `npx @tauri-apps/cli` or `cargo tauri` consistently |
