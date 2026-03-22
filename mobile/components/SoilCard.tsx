import { View, Text, StyleSheet } from "react-native";
import { colors, fonts } from "../constants/theme";

interface Props {
  soil: {
    recommended_ph: string;
    amendments: string[];
    drainage: string;
  };
}

export default function SoilCard({ soil }: Props) {
  return (
    <View style={styles.card}>
      <Text style={styles.sectionLabel}>Soil Health</Text>

      <View style={styles.row}>
        <Text style={styles.label}>Recommended pH</Text>
        <Text style={styles.value}>{soil.recommended_ph}</Text>
      </View>

      <View style={styles.row}>
        <Text style={styles.label}>Drainage</Text>
        <Text style={[styles.value, { flex: 1, textAlign: "right" }]} numberOfLines={2}>
          {soil.drainage}
        </Text>
      </View>

      {soil.amendments.length > 0 && (
        <>
          <Text style={styles.amendLabel}>Amendments</Text>
          {soil.amendments.map((a, i) => (
            <Text key={i} style={styles.amendItem}>
              • {a}
            </Text>
          ))}
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
  amendLabel: {
    fontFamily: fonts.bodyMedium,
    fontSize: 12,
    color: colors.text2,
    marginTop: 8,
    marginBottom: 4,
  },
  amendItem: {
    fontFamily: fonts.bodyFamily,
    fontSize: 14,
    color: colors.text1,
    marginBottom: 2,
    paddingLeft: 4,
  },
});
