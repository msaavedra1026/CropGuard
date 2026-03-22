import { useEffect, useRef } from "react";
import { View, Text, Animated, StyleSheet } from "react-native";
import { colors, fonts } from "../constants/theme";

interface DiseaseResult {
  name: string;
  confidence: number;
  severity: string;
  affected_percent: number;
  description: string;
}

interface Props {
  disease: DiseaseResult;
}

export default function DiagnosisCard({ disease }: Props) {
  const severityColor =
    colors.severity[disease.severity as keyof typeof colors.severity] ?? colors.text2;
  const pulseAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    if (disease.severity === "Critical") {
      Animated.sequence([
        Animated.timing(pulseAnim, { toValue: 1.15, duration: 200, useNativeDriver: true }),
        Animated.timing(pulseAnim, { toValue: 1, duration: 200, useNativeDriver: true }),
      ]).start();
    }
  }, []);

  return (
    <View style={styles.card}>
      <Text style={styles.sectionLabel}>Disease Detected</Text>
      <Text style={styles.diseaseName}>{disease.name}</Text>

      <View style={styles.row}>
        <Text style={styles.label}>Confidence</Text>
        <Text style={styles.value}>{Math.round(disease.confidence * 100)}%</Text>
      </View>

      <View style={styles.row}>
        <Text style={styles.label}>Severity</Text>
        <Animated.View
          style={[styles.badge, { backgroundColor: severityColor, transform: [{ scale: pulseAnim }] }]}
        >
          <Text style={styles.badgeText}>{disease.severity}</Text>
        </Animated.View>
      </View>

      {/* Affected percent bar */}
      <View style={styles.row}>
        <Text style={styles.label}>Affected Tissue</Text>
        <Text style={styles.value}>{disease.affected_percent}%</Text>
      </View>
      <View style={styles.barBg}>
        <View
          style={[
            styles.barFill,
            {
              width: `${Math.min(disease.affected_percent, 100)}%`,
              backgroundColor: severityColor,
            },
          ]}
        />
      </View>

      <Text style={styles.description}>{disease.description}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    marginHorizontal: 16,
    marginBottom: 12,
    borderRadius: 12,
    padding: 16,
  },
  sectionLabel: {
    fontFamily: fonts.bodyMedium,
    fontSize: 12,
    color: colors.accent,
    textTransform: "uppercase",
    letterSpacing: 1,
    marginBottom: 4,
  },
  diseaseName: {
    fontFamily: fonts.headerFamily,
    fontSize: 24,
    color: colors.text1,
    marginBottom: 12,
  },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  label: {
    fontFamily: fonts.bodyFamily,
    fontSize: 14,
    color: colors.text2,
  },
  value: {
    fontFamily: fonts.bodyMedium,
    fontSize: 14,
    color: colors.text1,
  },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  badgeText: {
    fontFamily: fonts.bodyMedium,
    fontSize: 12,
    color: colors.text1,
  },
  barBg: {
    height: 6,
    backgroundColor: colors.bg,
    borderRadius: 3,
    marginBottom: 12,
    overflow: "hidden",
  },
  barFill: {
    height: "100%",
    borderRadius: 3,
  },
  description: {
    fontFamily: fonts.bodyFamily,
    fontSize: 14,
    color: colors.text2,
    lineHeight: 20,
  },
});
