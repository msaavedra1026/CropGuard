import { View, Text, StyleSheet } from "react-native";
import { colors, fonts } from "../constants/theme";

interface Props {
  pests: {
    detected: boolean;
    type: string | null;
    severity: string | null;
    treatment: string | null;
  };
}

export default function PestCard({ pests }: Props) {
  if (!pests.detected) return null;

  const severityColor =
    colors.severity[(pests.severity ?? "Mild") as keyof typeof colors.severity] ?? colors.text2;

  return (
    <View style={styles.card}>
      <Text style={styles.sectionLabel}>Pest Alert</Text>
      <View style={styles.headerRow}>
        <Text style={styles.pestType}>{pests.type ?? "Unknown Pest"}</Text>
        {pests.severity && (
          <View style={[styles.badge, { backgroundColor: severityColor }]}>
            <Text style={styles.badgeText}>{pests.severity}</Text>
          </View>
        )}
      </View>
      {pests.treatment && (
        <>
          <Text style={styles.treatmentLabel}>Treatment</Text>
          <Text style={styles.treatmentText}>{pests.treatment}</Text>
        </>
      )}
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
    marginBottom: 8,
  },
  headerRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10,
  },
  pestType: {
    fontFamily: fonts.headerFamily,
    fontSize: 20,
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
  treatmentLabel: {
    fontFamily: fonts.bodyMedium,
    fontSize: 12,
    color: colors.text2,
    marginBottom: 2,
  },
  treatmentText: {
    fontFamily: fonts.bodyFamily,
    fontSize: 14,
    color: colors.text1,
    lineHeight: 20,
  },
});
