---
name: expo-react-native
description: Expo SDK 52 with EAS Build, React Native best practices, native modules, file-based routing, and app store deployment.
---

# Expo React Native

## Overview

Expo is a framework for building universal React Native apps for iOS, Android, and web. SDK 52 introduces the New Architecture by default, Expo Router v4, and improved native module support.

## Project Setup

```bash
# Create new Expo project
npx create-expo-app@latest MyApp --template blank-typescript

# With Expo Router (recommended)
npx create-expo-app@latest MyApp --template tabs

# Install EAS CLI
npm install -g eas-cli
eas login
eas build:configure
```

## app.json / app.config.ts

```typescript
// app.config.ts - Dynamic config with environment support
import { ExpoConfig, ConfigContext } from "expo/config";

export default ({ config }: ConfigContext): ExpoConfig => ({
  ...config,
  name: process.env.APP_ENV === "production" ? "MyApp" : "MyApp (Dev)",
  slug: "my-app",
  version: "1.0.0",
  orientation: "portrait",
  icon: "./assets/images/icon.png",
  scheme: "myapp",
  userInterfaceStyle: "automatic",

  splash: {
    image: "./assets/images/splash.png",
    resizeMode: "contain",
    backgroundColor: "#ffffff",
  },

  ios: {
    supportsTablet: true,
    bundleIdentifier: "com.mycompany.myapp",
    buildNumber: process.env.BUILD_NUMBER || "1",
    infoPlist: {
      NSCameraUsageDescription: "Camera is used for profile photos.",
      NSPhotoLibraryUsageDescription: "Photo library for selecting images.",
    },
    entitlements: {
      "com.apple.developer.associated-domains": ["applinks:example.com"],
    },
  },

  android: {
    package: "com.mycompany.myapp",
    versionCode: parseInt(process.env.BUILD_NUMBER || "1", 10),
    adaptiveIcon: {
      foregroundImage: "./assets/images/adaptive-icon.png",
      backgroundColor: "#ffffff",
    },
    permissions: ["android.permission.CAMERA", "android.permission.READ_EXTERNAL_STORAGE"],
  },

  web: {
    bundler: "metro",
    output: "static",
    favicon: "./assets/images/favicon.png",
  },

  plugins: [
    "expo-router",
    "expo-camera",
    [
      "expo-notifications",
      {
        icon: "./assets/images/notification-icon.png",
        color: "#ffffff",
        sounds: ["./assets/sounds/notification.wav"],
      },
    ],
    [
      "expo-build-properties",
      {
        ios: { newArchEnabled: true },
        android: { newArchEnabled: true },
      },
    ],
  ],

  experiments: { typedRoutes: true },

  extra: {
    apiUrl: process.env.API_URL || "https://api.example.com",
    eas: { projectId: "your-eas-project-id" },
  },
});
```

## Expo Router v4 File-Based Routing

```typescript
// app/_layout.tsx - Root layout
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { ThemeProvider } from "@/components/ThemeProvider";
import { AuthProvider } from "@/context/auth";

export default function RootLayout() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Stack screenOptions={{ headerShown: false }}>
          <Stack.Screen name="(auth)" options={{ animation: "fade" }} />
          <Stack.Screen name="(tabs)" />
          <Stack.Screen
            name="modal"
            options={{ presentation: "modal", animation: "slide_from_bottom" }}
          />
        </Stack>
        <StatusBar style="auto" />
      </AuthProvider>
    </ThemeProvider>
  );
}

// app/(tabs)/_layout.tsx - Tab navigation
import { Tabs } from "expo-router";
import { Platform } from "react-native";
import { HapticTab } from "@/components/HapticTab";
import { IconSymbol } from "@/components/ui/IconSymbol";

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: "#007AFF",
        headerShown: false,
        tabBarButton: HapticTab,
        tabBarStyle: Platform.select({
          ios: { position: "absolute" },
          default: {},
        }),
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: "Home",
          tabBarIcon: ({ color }) => <IconSymbol name="house.fill" color={color} />,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: "Profile",
          tabBarIcon: ({ color }) => <IconSymbol name="person.fill" color={color} />,
        }}
      />
    </Tabs>
  );
}

// app/(tabs)/index.tsx
import { Link, router } from "expo-router";

export default function HomeScreen() {
  return (
    <View>
      <Link href="/modal">Open Modal</Link>
      <Link href={{ pathname: "/users/[id]", params: { id: "123" } }}>
        View User
      </Link>
      <Button onPress={() => router.push("/settings")} title="Settings" />
    </View>
  );
}

// app/users/[id].tsx - Dynamic route
import { useLocalSearchParams } from "expo-router";

export default function UserScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  return <Text>User ID: {id}</Text>;
}
```

## Native Modules & APIs

```typescript
// Camera with expo-camera
import { CameraView, useCameraPermissions } from "expo-camera";
import { useState, useRef } from "react";

export function CameraScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const cameraRef = useRef<CameraView>(null);

  if (!permission?.granted) {
    return (
      <View>
        <Text>Camera access required</Text>
        <Button onPress={requestPermission} title="Grant Permission" />
      </View>
    );
  }

  const takePicture = async () => {
    const photo = await cameraRef.current?.takePictureAsync({
      quality: 0.8,
      base64: false,
      exif: false,
    });
    if (photo) uploadPhoto(photo.uri);
  };

  return (
    <CameraView ref={cameraRef} style={{ flex: 1 }} facing="back">
      <Button onPress={takePicture} title="Capture" />
    </CameraView>
  );
}

// Push Notifications
import * as Notifications from "expo-notifications";
import * as Device from "expo-device";
import Constants from "expo-constants";

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

async function registerForPushNotifications(): Promise<string | null> {
  if (!Device.isDevice) return null;

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== "granted") {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== "granted") return null;

  const token = await Notifications.getExpoPushTokenAsync({
    projectId: Constants.expoConfig?.extra?.eas?.projectId,
  });

  return token.data;
}

// Secure Storage
import * as SecureStore from "expo-secure-store";

await SecureStore.setItemAsync("auth_token", token);
const savedToken = await SecureStore.getItemAsync("auth_token");
await SecureStore.deleteItemAsync("auth_token");
```

## EAS Build Configuration

```json
// eas.json
{
  "cli": { "version": ">= 7.0.0" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": { "simulator": true },
      "env": { "APP_ENV": "development", "API_URL": "https://dev-api.example.com" }
    },
    "preview": {
      "distribution": "internal",
      "ios": { "simulator": false },
      "env": { "APP_ENV": "staging", "API_URL": "https://staging-api.example.com" }
    },
    "production": {
      "autoIncrement": true,
      "env": { "APP_ENV": "production", "API_URL": "https://api.example.com" }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "developer@example.com",
        "ascAppId": "1234567890",
        "appleTeamId": "ABC123XYZ"
      },
      "android": {
        "serviceAccountKeyPath": "./google-service-account.json",
        "track": "production"
      }
    }
  }
}
```

```bash
# Build commands
eas build --platform ios --profile development
eas build --platform android --profile preview
eas build --platform all --profile production

# Submit to stores
eas submit --platform ios --profile production
eas submit --platform android --profile production

# OTA updates (no store review needed)
eas update --branch production --message "Fix login bug"
```

## Performance Patterns

```typescript
// Use FlashList instead of FlatList for large lists
import { FlashList } from "@shopify/flash-list";

function ProductList({ products }) {
  return (
    <FlashList
      data={products}
      estimatedItemSize={100}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => <ProductCard product={item} />}
      onEndReached={loadMore}
      onEndReachedThreshold={0.5}
    />
  );
}

// Memoize expensive components
const ProductCard = React.memo(({ product }) => {
  return (
    <View>
      <Image source={{ uri: product.image }} />
      <Text>{product.name}</Text>
    </View>
  );
});

// React Query for data fetching
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

function useProducts() {
  return useQuery({
    queryKey: ["products"],
    queryFn: () => api.getProducts(),
    staleTime: 5 * 60 * 1000,  // 5 minutes
  });
}

// Zustand for global state
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import AsyncStorage from "@react-native-async-storage/async-storage";

const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,
      setUser: (user, token) => set({ user, token }),
      logout: () => set({ user: null, token: null }),
    }),
    {
      name: "auth-storage",
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);
```

## Key Patterns

- **New Architecture** is default in SDK 52 — JSI-based native modules are faster
- **`expo-router`** file-based routing eliminates navigation boilerplate
- **EAS Build** handles signing, provisioning profiles, and certificates
- **EAS Update** for over-the-air JS updates without app store review
- **`FlashList`** over `FlatList` for 10x better list performance
- **`expo-secure-store`** for tokens, `AsyncStorage` only for non-sensitive data

## Models to Use

- **claude-opus-4-5**: Complex navigation architectures, native module bridging, performance optimization
- **claude-sonnet-4-5**: Screen development, EAS configuration, state management
- **claude-haiku-3-5**: Simple component creation, style adjustments, basic API calls
