import { useState } from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { colors, fonts } from "../constants/theme";

interface NutrientRecommendation {
  nutrient: string;
  symptom: string;
  treatment: string;
  frequency: string;
  organic_option: string;
}

interface Props {
  nutrients: {
    deficiencies: string[];
    recommendations: NutrientRecommendation[];
  };
}

function NutrientItem({ rec }: { rec: NutrientRecommendation }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <TouchableOpacity style={styles.nutrientItem} onPress={() => setExpanded(!expanded)}>
      <View style={styles.nutrientHeader}>
        <Text style={styles.nutrientName}>{rec.nutrient} Deficiency</Text>
        <Text style={styles.chevron}>{expanded ? "▾" : "▸"}</Text>
      </View>
      {expanded && (
        <View style={styles.nutrientBody}>
          <Text style={styles.detailLabel}>Symptom</Text>
          <Text style={styles.detailValue}>{rec.symptom}</Text>
          <Text style={styles.detailLabel}>Treatment</Text>
          <Text style={styles.detailValue}>{rec.treatment}</Text>
          <Text style={styles.detailLabel}>Frequency</Text>
          <Text style={styles.detailValue}>{rec.frequency}</Text>
          <Text style={styles.detailLabel}>Organic Alternative</Text>
          <Text style={styles.detailValue}>{rec.organic_option}</Text>
        </View>
      )}
    </TouchableOpacity>
  );
}

export default function NutrientSection({ nutrients }: Props) {
  if (nutrients.deficiencies.length === 0) return null;

  return (
    <View style={styles.card}>
      <Text style={styles.sectionLabel}>Nutrient Analysis</Text>
      <Text style={styles.deficiencyList}>
        Deficiencies: {nutrients.deficiencies.join(", ")}
      </Text>
      {nutrients.recommendations.map((rec) => (
        <NutrientItem key={rec.nutrient} rec={rec} />
      ))}
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
  deficiencyList: {
    fontFamily: fonts.bodyMedium,
    fontSize: 14,
    color: colors.text1,
    marginBottom: 12,
  },
  nutrientItem: {
    backgroundColor: colors.bg,
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
  },
  nutrientHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  nutrientName: {
    fontFamily: fonts.headerFamily,
    fontSize: 16,
    color: colors.text1,
  },
  chevron: {
    fontSize: 16,
    color: colors.text2,
  },
  nutrientBody: { marginTop: 10 },
  detailLabel: {
    fontFamily: fonts.bodyMedium,
    fontSize: 12,
    color: colors.accent,
    marginTop: 6,
  },
  detailValue: {
    fontFamily: fonts.bodyFamily,
    fontSize: 14,
    color: colors.text2,
    marginTop: 2,
  },
});
