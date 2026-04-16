---
name: android-deploy
cluster: mobile
description: "Android: Gradle variants, signing, Google Play Console, Firebase App Distribution, Fastlane, bundletool"
tags: ["deployment","playstore","fastlane","android"]
dependencies: []
composes: []
similar_to: []
called_by: []
authorization_required: false
scope: general
model_hint: claude-sonnet
embedding_hint: "android deploy play store signing fastlane firebase ci bundletool"
---

## android-deploy

### Purpose
This skill automates Android app deployment, covering Gradle-based builds, APK/AAB signing, uploads to Google Play Console, distribution via Firebase, and tools like Fastlane and bundletool for streamlined CI/CD.

### When to Use
Use this skill for deploying Android apps in production, testing variants, or automating releases; ideal for CI pipelines, app updates to Google Play, or internal distribution via Firebase; avoid for non-Android projects or basic builds without deployment needs.

### Key Capabilities
- Build and select Gradle variants (e.g., debug, release) using build.gradle configurations.
- Sign APKs or AABs with keystores, supporting v1 and v2 signing schemes.
- Upload apps to Google Play Console via API, including managing edits and tracks.
- Distribute builds via Firebase App Distribution for beta testing.
- Automate workflows with Fastlane, including lane definitions for build and deploy.
- Generate and test APKs from AABs using bundletool for device-specific optimization.

### Usage Patterns
To deploy an Android app, first configure build.gradle with variants (e.g., set `buildTypes { release { ... } }`), then use Fastlane to chain tasks like building, signing, and uploading. For CI integration, invoke Gradle tasks via scripts, pass environment variables for keys, and handle outputs for subsequent steps. Always verify keystore paths and API credentials before running; for example, run a Fastlane lane that calls `./gradlew assembleRelease` followed by bundletool extraction.

### Common Commands/API
- Gradle build for a variant: `./gradlew assembleRelease --stacktrace` (use `--stacktrace` for debugging).
- Sign an APK: `apksigner sign --ks my.keystore --ks-key-alias myalias myapp.apk` (requires keystore file and alias).
- Upload to Google Play: Use Google Play API endpoint `POST https://www.googleapis.com/androidpublisher/v3/applications/{packageName}/edits` with OAuth token from `$GOOGLE_PLAY_API_KEY`; example curl: `curl -H "Authorization: Bearer $GOOGLE_PLAY_API_KEY" -d '{"title": "Edit"}' https://...`.
- Firebase App Distribution: `firebase appdistribution:distribute myapp.apk --app <APP_ID> --groups my-testers` (set `$FIREBASE_TOKEN` for auth).
- Fastlane lane: Define in Fastfile: `lane :deploy do |options| sh("./gradlew assembleRelease") end`; run with `fastlane android deploy`.
- Bundletool for AAB: `bundletool build-apks --bundle=myapp.aab --output=myapp.apks --ks=my.keystore` (include `--ks-pass` for password via env var like `$KEYSTORE_PASS`).
- Code snippet for Gradle build in build.gradle: `android { buildTypes { release { signingConfig signingConfigs.release } } }` (2 lines).
- API call in script: `response = requests.post('https://www.googleapis.com/androidpublisher/v3/...', headers={'Authorization': f'Bearer {os.environ["GOOGLE_PLAY_API_KEY"]}'} )` (2 lines).

### Integration Notes
Integrate by setting environment variables for sensitive data, e.g., `export GOOGLE_PLAY_API_KEY=$SERVICE_API_KEY` for OAuth; configure Fastlane with a Fastfile in your project root, including lanes that reference Gradle tasks. For Firebase, add the Firebase CLI and set `$FIREBASE_TOKEN` via service account JSON. Use bundletool as a JAR in your build pipeline, ensuring it's version-compatible (e.g., 1.14.0+). Link with CI tools like GitHub Actions by adding steps: `run: fastlane android deploy` in your workflow YAML.

### Error Handling
Handle signing errors by checking keystore paths and passwords (e.g., if `apksigner` fails with "Keystore not found", verify file existence); for API uploads, catch 401 errors by ensuring `$GOOGLE_PLAY_API_KEY` is valid and not expired. Gradle build failures often stem from variant mismatches—use `./gradlew tasks` to list available tasks. For Fastlane, debug with `fastlane --verbose`; if bundletool reports "Invalid bundle", validate AAB with `bundletool validate --bundle=myapp.aab`. Always wrap commands in try-catch blocks in scripts, e.g., `try { sh("./gradlew assembleRelease") } catch { echo "Build failed: $error" }`.

### Concrete Usage Examples
**Example 1: Build and Sign an APK for Release**  
First, ensure build.gradle has: `signingConfigs { release { storeFile file("my.keystore") keyAlias "myalias" } }`. Then, run: `./gradlew assembleRelease`. Finally, sign: `apksigner sign --ks my.keystore --ks-key-alias myalias app/build/outputs/apk/release/app-release-unsigned.apk`. This produces a signed APK ready for distribution.

**Example 2: Upload to Google Play via Fastlane**  
Create a Fastfile with: `lane :upload do upload_to_play_store track: 'internal' apk_path: 'app/build/outputs/apk/release/app-release.apk' end`. Set env var: `export SUPPLY_JSON_KEY_FILE=$GOOGLE_PLAY_SERVICE_ACCOUNT`. Run: `fastlane upload`. This automates building, signing, and uploading to the internal track on Google Play Console.

### Graph Relationships
- Related to: mobile cluster (e.g., shares dependencies with iOS deployment skills).
- Integrates with: ci-cd pipelines (e.g., connects to build tools like Gradle).
- Depends on: authentication services (e.g., Google Play API keys).
- Conflicts with: non-mobile skills (e.g., web deployment).
