import { useRef, useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from "react-native";
import { CameraView, useCameraPermissions } from "expo-camera";
import * as ImagePicker from "expo-image-picker";
import { useRouter } from "expo-router";
import { useScanStore } from "../stores/scanStore";
import { colors, fonts } from "../constants/theme";

export default function CameraScreen() {
  const router = useRouter();
  const cameraRef = useRef<CameraView>(null);
  const [permission, requestPermission] = useCameraPermissions();
  const { isAnalyzing, startAnalysis, currentResult, error } = useScanStore();
  const [cameraReady, setCameraReady] = useState(false);

  // Watch for result to navigate
  useScanStore.subscribe((state) => {
    if (state.currentResult && !state.isAnalyzing) {
      router.push({ pathname: "/result", params: { scan_id: state.currentResult.scan_id } });
    }
  });

  const handleCapture = async () => {
    if (!cameraRef.current || !cameraReady) return;
    try {
      const photo = await cameraRef.current.takePictureAsync({ quality: 0.8 });
      if (photo?.uri) {
        await startAnalysis(photo.uri);
      }
    } catch (err) {
      Alert.alert("Capture failed", "Please try again.");
    }
  };

  const handlePickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.8,
    });
    if (!result.canceled && result.assets[0]) {
      await startAnalysis(result.assets[0].uri);
    }
  };

  if (!permission) return <View style={styles.container} />;

  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.permissionText}>Camera access is needed to scan your crops</Text>
        <TouchableOpacity style={styles.permissionBtn} onPress={requestPermission}>
          <Text style={styles.permissionBtnText}>Grant Permission</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <CameraView
        ref={cameraRef}
        style={StyleSheet.absoluteFill}
        facing="back"
        onCameraReady={() => setCameraReady(true)}
      />

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>CropGuard</Text>
        <TouchableOpacity onPress={() => router.push("/history")}>
          <Text style={styles.historyLink}>History</Text>
        </TouchableOpacity>
      </View>

      {/* Analyzing overlay */}
      {isAnalyzing && (
        <View style={styles.analyzingOverlay}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={styles.analyzingText}>CropGuard is analyzing your crop...</Text>
        </View>
      )}

      {/* Error display */}
      {error && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {/* Bottom controls */}
      <View style={styles.bottomBar}>
        <TouchableOpacity style={styles.uploadBtn} onPress={handlePickImage}>
          <Text style={styles.uploadText}>Upload Photo</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.captureBtn, isAnalyzing && styles.captureBtnDisabled]}
          onPress={handleCapture}
          disabled={isAnalyzing}
        >
          <View style={styles.captureInner} />
        </TouchableOpacity>

        <View style={{ width: 80 }} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bg,
    justifyContent: "center",
    alignItems: "center",
  },
  header: {
    position: "absolute",
    top: 60,
    left: 20,
    right: 20,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    zIndex: 10,
  },
  title: {
    fontFamily: fonts.headerFamily,
    fontSize: 28,
    color: colors.primary,
  },
  historyLink: {
    fontFamily: fonts.bodyMedium,
    fontSize: 16,
    color: colors.accent,
  },
  bottomBar: {
    position: "absolute",
    bottom: 40,
    left: 0,
    right: 0,
    flexDirection: "row",
    justifyContent: "space-around",
    alignItems: "center",
    paddingHorizontal: 20,
  },
  captureBtn: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 4,
    borderColor: colors.text1,
    justifyContent: "center",
    alignItems: "center",
  },
  captureBtnDisabled: {
    opacity: 0.4,
  },
  captureInner: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: colors.text1,
  },
  uploadBtn: {
    backgroundColor: colors.surface,
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
  },
  uploadText: {
    fontFamily: fonts.bodyMedium,
    fontSize: 14,
    color: colors.text2,
  },
  analyzingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "rgba(28, 26, 20, 0.85)",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 20,
  },
  analyzingText: {
    fontFamily: fonts.bodyMedium,
    fontSize: 18,
    color: colors.text1,
    marginTop: 16,
  },
  errorBanner: {
    position: "absolute",
    top: 110,
    left: 20,
    right: 20,
    backgroundColor: "#F44336",
    padding: 12,
    borderRadius: 8,
    zIndex: 15,
  },
  errorText: {
    fontFamily: fonts.bodyFamily,
    fontSize: 14,
    color: colors.text1,
    textAlign: "center",
  },
  permissionText: {
    fontFamily: fonts.bodyFamily,
    fontSize: 16,
    color: colors.text2,
    textAlign: "center",
    marginBottom: 16,
    paddingHorizontal: 40,
  },
  permissionBtn: {
    backgroundColor: colors.primary,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  permissionBtnText: {
    fontFamily: fonts.bodyMedium,
    fontSize: 16,
    color: colors.text1,
  },
});
