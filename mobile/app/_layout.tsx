import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import {
  useFonts,
  ZillaSlab_700Bold,
} from "@expo-google-fonts/zilla-slab";
import {
  DMSans_400Regular,
  DMSans_500Medium,
} from "@expo-google-fonts/dm-sans";
import { View, ActivityIndicator } from "react-native";
import { colors } from "../constants/theme";

export default function RootLayout() {
  const [fontsLoaded] = useFonts({
    ZillaSlab_700Bold,
    DMSans_400Regular,
    DMSans_500Medium,
  });

  if (!fontsLoaded) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  return (
    <>
      <StatusBar style="light" />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: colors.bg },
          headerTintColor: colors.text1,
          headerTitleStyle: { fontFamily: "ZillaSlab_700Bold" },
          contentStyle: { backgroundColor: colors.bg },
        }}
      >
        <Stack.Screen name="index" options={{ headerShown: false }} />
        <Stack.Screen name="result" options={{ title: "Diagnosis" }} />
        <Stack.Screen name="history" options={{ title: "Scan History" }} />
      </Stack>
    </>
  );
}
