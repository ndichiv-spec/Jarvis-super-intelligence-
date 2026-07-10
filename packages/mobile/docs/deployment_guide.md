# Deployment Guide

## Prerequisites

- Flutter SDK ^3.4.0
- Android SDK (for Android builds)
- Xcode 15+ (for iOS builds)
- Apple Developer account (for iOS distribution)
- Google Play Console account (for Android distribution)

## Environment Configuration

1. Set the gateway URL in `lib/core/constants/api_constants.dart`:

```dart
static const String defaultBaseUrl = 'https://api.jarvis.ai';
```

2. Configure app version in `pubspec.yaml`:

```yaml
version: 1.0.0+1
```

## Android Build

### Release Build
```bash
flutter build apk --release
# or for app bundle
flutter build appbundle --release
```

### Signing
1. Create a keystore
2. Configure signing in `android/app/build.gradle`
3. Build signed APK/AAB

### Google Play
1. Create app in Google Play Console
2. Upload AAB to Internal Testing track
3. Promote through test tracks to production

## iOS Build

### Release Build
```bash
flutter build ios --release
```

### Distribution
1. Open `ios/Runner.xcworkspace` in Xcode
2. Configure signing team
3. Archive via Product → Archive
4. Upload to App Store Connect
5. Submit for review

## App Store Metadata

### Description
JARVIS Mobile is the official mobile companion for the JARVIS AI Ecosystem. Access your AI workspace, manage projects, browse knowledge, and monitor automations from anywhere.

### Keywords
AI, assistant, productivity, automation, knowledge management

### Privacy Policy URL
Configure in App Store Connect / Google Play Console

## Versioning

Follow semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes to API contracts
- MINOR: New features, backward-compatible
- PATCH: Bug fixes, performance improvements

## Post-Deployment

1. Monitor crash reports via platform crash reporting
2. Review analytics for feature adoption
3. Plan next update cycle based on feedback

## Rollback

1. Google Play: Deactivate problematic version, promote previous version
2. App Store: Remove build from review, re-submit previous version
