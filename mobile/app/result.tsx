import { useEffect, useState } from "react";
import { View, Text, ScrollView, StyleSheet, ActivityIndicator } from "react-native";
import { useLocalSearchParams } from "expo-router";
import { useScanStore, ScanResult } from "../stores/scanStore";
import { BACKEND_URL } from "../constants/api";
import { colors, fonts } from "../constants/theme";
import MaskOverlay from "../components/MaskOverlay";
import DiagnosisCard from "../components/DiagnosisCard";
import NutrientSection from "../components/NutrientSection";
import WateringCard from "../components/WateringCard";
import PestCard from "../components/PestCard";
import SoilCard from "../components/SoilCard";
import CareTimeline from "../components/CareTimeline";

export default function ResultScreen() {
  const { scan_id } = useLocalSearchParams<{ scan_id: string }>();
  const storeResult = useScanStore((s) => s.currentResult);
  const [result, setResult] = useState<ScanResult | null>(storeResult);
  const [loading, setLoading] = useState(!storeResult);

  useEffect(() => {
    if (storeResult?.scan_id === scan_id) {
      setResult(storeResult);
      setLoading(false);
      return;
    }
    // Fetch from server if not in store
    (async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/history/${scan_id}`);
        const data = await res.json();
        setResult(data);
      } catch {
        // stay loading
      } finally {
        setLoading(false);
      }
    })();
  }, [scan_id]);

  if (loading || !result) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Image + Mask Overlay */}
      <MaskOverlay scanId={result.scan_id} />

      {/* Crop type header */}
      <Text style={styles.cropType}>{result.crop_type}</Text>
      <Text style={styles.outlook}>{result.recovery_outlook}</Text>

      {/* Care sections */}
      <DiagnosisCard disease={result.disease} />
      <NutrientSection nutrients={result.nutrients} />
      <WateringCard watering={result.watering} />
      {result.pests.detected && <PestCard pests={result.pests} />}
      <SoilCard soil={result.soil} />
      <CareTimeline carePlan={result.care_plan} scanId={result.scan_id} />

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  content: { paddingBottom: 40 },
  loadingContainer: {
    flex: 1,
    backgroundColor: colors.bg,
    justifyContent: "center",
    alignItems: "center",
  },
  cropType: {
    fontFamily: fonts.headerFamily,
    fontSize: 32,
    color: colors.text1,
    marginHorizontal: 16,
    marginTop: 12,
  },
  outlook: {
    fontFamily: fonts.bodyFamily,
    fontSize: 14,
    color: colors.primary,
    marginHorizontal: 16,
    marginTop: 4,
    marginBottom: 16,
  },
});
