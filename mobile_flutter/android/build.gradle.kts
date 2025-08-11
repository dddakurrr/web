buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath("com.android.tools.build:gradle:7.4.2")
        classpath("org.jetbrains.kotlin:kotlin-gradle-plugin:1.8.10")
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

subprojects {
    afterEvaluate {
        if (extensions.findByName("android") != null) {
            extensions.configure<com.android.build.gradle.BaseExtension> {
                ndkVersion = "26.3.11579264"
            }
        }
    }
}

tasks.register<Delete>("clean") {
    delete(rootProject.buildDir)
}
