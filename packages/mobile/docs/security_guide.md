# Security Guide

## Overview

JARVIS Mobile implements defense-in-depth security controls aligned with the JARVIS Security Platform (Phase 12).

## Authentication

### Session-Based Auth
1. User provides email/password via `LoginPage`
2. Gateway authenticates against the Security Platform
3. Gateway returns `SessionModel` with token, refreshToken, expiry
4. Tokens stored in `FlutterSecureStorage` (platform-native encrypted storage)
5. `x-session-id` header sent with all subsequent requests

### Biometric Authentication
1. Device supports biometrics → `BiometricAuth` checks availability
2. User can enable biometric unlock in Settings
3. On subsequent launches, biometric prompt replaces password entry
4. Uses `local_auth` package with `biometricOnly: true` and `stickyAuth: true`

### Session Restoration
1. App stores session token in secure storage
2. On launch, `AuthNotifier.restoreSession()` checks for existing token
3. If valid, user proceeds to HomePage without re-authentication

## Authorization

All authorization decisions are made server-side by the Security Platform. The mobile app passes identity context via headers and respects HTTP 401/403 responses.

## Secure Storage

| Data | Storage | Encryption |
|------|---------|------------|
| Session token | FlutterSecureStorage | AES-256 (platform-native) |
| Refresh token | FlutterSecureStorage | AES-256 (platform-native) |
| Workspace ID | FlutterSecureStorage | AES-256 (platform-native) |
| Subject ID | FlutterSecureStorage | AES-256 (platform-native) |
| Cached data | SQLite | Device-level encryption |
| Preferences | SharedPreferences | Unencrypted (user prefs only) |

## Privacy Controls

| Capability | Policy |
|------------|--------|
| Location | Never tracked continuously |
| Camera | Only accessed on explicit user action |
| Microphone | Requires explicit permission |
| Photo upload | Never automatic |
| Contacts | Requires user approval |
| Device info | Minimal collection |

## Security Center

The `SecurityPage` provides:
- Active session list and revocation
- Device management (register, trust, remove)
- Biometric unlock toggle (in Settings)
- Security notifications

## Session Management

- Sessions expire after 30 minutes of inactivity (configurable)
- Refresh tokens enable silent re-authentication
- Sessions can be revoked from the Security Center or server-side
- All sensitive operations require an active session
