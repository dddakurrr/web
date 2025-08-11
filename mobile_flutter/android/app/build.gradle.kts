plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.mobile_flutter"
    compileSdk = 33
    ndkVersion = "26.3.11579264"

    defaultConfig {
        applicationId = "com.example.mobile_flutter"
        minSdk = 21
        targetSdk = 33
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        getByName("release") {
            signingConfig = signingConfigs.getByName("debug")
        }
    }
}

dependencies {
    implementation("org.jetbrains.kotlin:kotlin-stdlib:1.8.10")
}

// Inject Flutter Gradle manually
apply {
    from("${project(":flutter").projectDir}/packages/flutter_tools/gradle/flutter.gradle")
}
