# 📱 Build the SSAS Android APK

This folder is a **Capacitor 6** wrapper that turns the SSAS web platform
into a standalone native Android app.

The native shell loads your deployed Flask app inside a fullscreen WebView,
with a native splash screen, app icon, status-bar styling, and Android
back-button handling — installed users never see a browser chrome.

---

## 1. What's in this folder

```
mobile/
├── android/                  ← native Android Studio project (auto-generated)
│   └── app/src/main/
│       ├── AndroidManifest.xml
│       ├── java/.../MainActivity.java
│       └── res/              ← icons, splash, strings, colors
├── www/index.html            ← bridge loader (briefly visible at startup)
├── resources/
│   ├── icon.png              ← 1024×1024 floral icon (source)
│   └── splash.png            ← floral splash (source)
├── capacitor.config.json     ← APP CONFIG (edit `server.url`!)
├── package.json
└── BUILD_APK.md              ← (this file)
```

---

## 2. One-time setup on your computer

You **cannot** build an APK on Replit — Android requires the Android SDK
and a Java toolchain. Build it on your laptop:

1. **Install Android Studio** → <https://developer.android.com/studio>
   (it bundles the SDK, build-tools and a JDK).
2. Install **Node 18+** → <https://nodejs.org>.
3. Open Android Studio → *More actions → SDK Manager* and install
   "Android 13 (API 33)" platform + "Android SDK Build-Tools".
4. Set the env var (Linux/macOS, in `~/.zshrc` or `~/.bashrc`):
   ```bash
   export ANDROID_HOME="$HOME/Android/Sdk"
   export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"
   ```
   On Windows: System Properties → Environment Variables → set
   `ANDROID_HOME` to `C:\Users\<you>\AppData\Local\Android\Sdk`.

---

## 3. Get the project on your machine

From Replit, click **⋮ → Download as ZIP**, unzip it, then in a terminal:

```bash
cd <unzipped>/mobile
npm install
```

---

## 4. Point the app at your live server (IMPORTANT)

Open `mobile/capacitor.config.json` and replace:

```json
"server": {
  "url": "https://REPLACE-ME.replit.app",
   ...
}
```

with the **exact public HTTPS URL** of your deployed Flask app
(e.g. the URL shown after you click **Publish** in Replit). The native
shell loads everything from that URL — login, chats, AI theming, etc.

> If you ever change the URL, just edit this file and run `npx cap sync android`.

---

## 5. (Optional) Refresh the icon & splash

The icon and splash are already generated for every Android density
under `android/app/src/main/res/mipmap-*` and `drawable-*`. To regenerate
them after replacing `resources/icon.png` or `resources/splash.png`:

```bash
npm run icons          # cordova-res android --skip-config --copy
npx cap sync android
```

---

## 6. Build the debug APK

```bash
npx cap sync android       # copies config + plugins into android/
cd android
./gradlew assembleDebug    # Windows: gradlew.bat assembleDebug
```

The APK lands at:

```
mobile/android/app/build/outputs/apk/debug/app-debug.apk
```

Install on a phone via USB (USB-debugging on, then `adb install app-debug.apk`)
or just copy the file to the phone and tap it.

---

## 7. Build a signed release APK / Play Store bundle

1. Generate a keystore (one-time):
   ```bash
   keytool -genkey -v -keystore ssas-release.keystore \
           -keyalg RSA -keysize 2048 -validity 10000 -alias ssas
   ```
2. Create `android/key.properties`:
   ```properties
   storeFile=/absolute/path/to/ssas-release.keystore
   storePassword=YOUR_STORE_PASSWORD
   keyAlias=ssas
   keyPassword=YOUR_KEY_PASSWORD
   ```
3. In `android/app/build.gradle`, above `android { … }` add:
   ```gradle
   def keystoreProperties = new Properties()
   def keystorePropertiesFile = rootProject.file('key.properties')
   if (keystorePropertiesFile.exists()) {
     keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
   }
   ```
   Inside `android { … }`:
   ```gradle
   signingConfigs {
     release {
       storeFile file(keystoreProperties['storeFile'])
       storePassword keystoreProperties['storePassword']
       keyAlias keystoreProperties['keyAlias']
       keyPassword keystoreProperties['keyPassword']
     }
   }
   buildTypes { release { signingConfig signingConfigs.release } }
   ```
4. Build:
   ```bash
   cd android
   ./gradlew assembleRelease   # → app-release.apk
   ./gradlew bundleRelease     # → app-release.aab (Play Store)
   ```

---

## 8. Open in Android Studio (optional but recommended)

```bash
npx cap open android
```

This launches Android Studio on the `android/` folder so you can run on
an emulator, hot-reload, or sign builds via the GUI (*Build → Generate
Signed Bundle / APK*).

---

## 9. iOS

```bash
npx cap add ios
npx cap open ios            # requires macOS + Xcode
```

The same `capacitor.config.json` works.

---

## 10. Troubleshooting

| Symptom | Fix |
|---|---|
| White screen on launch | `server.url` in `capacitor.config.json` is wrong or unreachable |
| Mixed-content blocked | Ensure your server is **HTTPS** (Replit deployments are by default) |
| Login redirect fails | Add the OAuth callback host to `server.allowNavigation` |
| "SDK location not found" | Create `android/local.properties` with `sdk.dir=/path/to/Android/Sdk` |
| Gradle out of memory | `echo "org.gradle.jvmargs=-Xmx4g" >> android/gradle.properties` |
