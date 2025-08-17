import type { ExpoConfig } from "expo/config";

const config: ExpoConfig = {
  name: "Meffec",
  slug: "meffec",
  version: "1.0.0",
  scheme: "myapp",
  orientation: "portrait",
  userInterfaceStyle: "automatic",

  icon: "./assets/images/icon.png",
  splash: {
    image: "./assets/images/splash.png",
    resizeMode: "contain",
    backgroundColor: "#ffffff",
  },

  ios: {
    supportsTablet: true,
    bundleIdentifier: "com.mervinvb.Meffec",
  },

  android: {
    package: "com.mervinvb.Meffec",
    adaptiveIcon: {
      foregroundImage: "./assets/images/icon.png",
      backgroundColor: "#ffffff",
    },
  },

  web: {
    bundler: "metro",
    output: "static",
    favicon: "./assets/images/favicon.png",
  },

  plugins: [
    "expo-router",
    [
      "expo-font",
      {
        fonts: ["./assets/fonts/inter.ttf"],
      },
    ],
  ],

  experiments: {
    typedRoutes: true,
  },
};

export default config;
