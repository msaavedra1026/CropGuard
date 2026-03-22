import { useEffect, useRef } from "react";
import { View, Text, Animated, StyleSheet } from "react-native";
import { colors, fonts } from "../constants/theme";

interface Props {
  watering: {
    current_status: string;
    schedule: string;
    amount_ml_per_plant: number;
    warning: string | null;
  };
}

function statusToPercent(status: string): number {
  const lower = status.toLowerCase();
  if (lower.includes("overwater")) return 90;
  if (lower.includes("well water") || lower.includes("adequate")) return 70;
  if (lower.includes("slightly under")) return 40;
  if (lower.includes("underwater") || lower.includes("dry")) return 20;
  return 50;
}

export default function WateringCard({ watering }: Props) {
  const fillAnim = useRef(new Animated.Value(0)).current;
  const percent = statusToPercent(watering.current_status);

  useEffect(() => {
    Animated.timing(fillAnim, {
      toValue: percent,
      duration: 800,
      useNativeDriver: false,
    }).start();
  }, [percent]);

  const fillHeight = fillAnim.interpolate({
    inputRange: [0, 100],
    outputRange: ["0%", "100%"],
  });

  return (
    <View style={styles.card}>
      <Text style={styles.sectionLabel}>Watering</Text>

      <View style={styles.row}>
        {/* Water level indicator */}
        <View style={styles.waterTank}>
          <Animated.View style={[styles.waterFill, { height: fillHeight }]} />
          <Text style={styles.waterPercent}>{percent}%</Text>
        </View>

        <View style={styles.info}>
          <Text style={styles.statusText}>{watering.current_status}</Text>
          <Text style={styles.scheduleText}>{watering.schedule}</Text>
          <Text style={styles.amountText}>{watering.amount_ml_per_plant} ml per plant</Text>
        </View>
      </View>

      {watering.warning && (
        <View style={styles.warningBox}>
          <Text style={styles.warningText}>{watering.warning}</Text>
        </View>
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
  row: { flexDirection: "row", alignItems: "center" },
  waterTank: {
    width: 50,
    height: 80,
    backgroundColor: colors.bg,
    borderRadius: 8,
    overflow: "hidden",
    justifyContent: "flex-end",
    alignItems: "center",
    marginRight: 16,
  },
  waterFill: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: "#4FC3F7",
    borderRadius: 4,
  },
  waterPercent: {
    fontFamily: fonts.bodyMedium,
    fontSize: 12,
    color: colors.text1,
    zIndex: 1,
    marginBottom: 4,
  },
  info: { flex: 1 },
  statusText: {
    fontFamily: fonts.headerFamily,
    fontSize: 18,
    color: colors.text1,
    marginBottom: 4,
  },
  scheduleText: {
    fontFamily: fonts.bodyFamily,
    fontSize: 14,
    color: colors.text2,
    marginBottom: 2,
  },
  amountText: {
    fontFamily: fonts.bodyMedium,
    fontSize: 14,
    color: colors.primary,
  },
  warningBox: {
    backgroundColor: "rgba(245, 166, 35, 0.15)",
    borderRadius: 8,
    padding: 10,
    marginTop: 12,
  },
  warningText: {
    fontFamily: fonts.bodyFamily,
    fontSize: 13,
    color: colors.accent,
  },
});
