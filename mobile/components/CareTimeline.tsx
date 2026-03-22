import { useEffect, useState } from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { colors, fonts } from "../constants/theme";

interface Props {
  carePlan: {
    immediate: string[];
    this_week: string[];
    ongoing: string[];
  };
  scanId: string;
}

function CheckableItem({
  text,
  storageKey,
}: {
  text: string;
  storageKey: string;
}) {
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    AsyncStorage.getItem(storageKey).then((v) => {
      if (v === "true") setChecked(true);
    });
  }, []);

  const toggle = async () => {
    const next = !checked;
    setChecked(next);
    await AsyncStorage.setItem(storageKey, String(next));
  };

  return (
    <TouchableOpacity style={styles.item} onPress={toggle}>
      <View style={[styles.checkbox, checked && styles.checkboxChecked]}>
        {checked && <Text style={styles.checkmark}>✓</Text>}
      </View>
      <Text style={[styles.itemText, checked && styles.itemTextChecked]}>{text}</Text>
    </TouchableOpacity>
  );
}

export default function CareTimeline({ carePlan, scanId }: Props) {
  const columns = [
    { title: "Today", items: carePlan.immediate, color: "#F44336" },
    { title: "This Week", items: carePlan.this_week, color: colors.accent },
    { title: "Ongoing", items: carePlan.ongoing, color: colors.primary },
  ];

  return (
    <View style={styles.card}>
      <Text style={styles.sectionLabel}>Care Timeline</Text>
      <View style={styles.columns}>
        {columns.map((col) => (
          <View key={col.title} style={styles.column}>
            <View style={[styles.colHeader, { borderBottomColor: col.color }]}>
              <Text style={styles.colTitle}>{col.title}</Text>
            </View>
            {col.items.map((item, i) => (
              <CheckableItem
                key={i}
                text={item}
                storageKey={`care_${scanId}_${col.title}_${item}`}
              />
            ))}
          </View>
        ))}
      </View>
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
  columns: { flexDirection: "row", gap: 8 },
  column: { flex: 1 },
  colHeader: {
    borderBottomWidth: 2,
    paddingBottom: 6,
    marginBottom: 8,
  },
  colTitle: {
    fontFamily: fonts.bodyMedium,
    fontSize: 13,
    color: colors.text1,
  },
  item: {
    flexDirection: "row",
    alignItems: "flex-start",
    marginBottom: 8,
  },
  checkbox: {
    width: 18,
    height: 18,
    borderRadius: 4,
    borderWidth: 1.5,
    borderColor: colors.text2,
    marginRight: 6,
    justifyContent: "center",
    alignItems: "center",
    marginTop: 1,
  },
  checkboxChecked: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  checkmark: {
    fontSize: 12,
    color: colors.text1,
  },
  itemText: {
    fontFamily: fonts.bodyFamily,
    fontSize: 12,
    color: colors.text2,
    flex: 1,
    lineHeight: 16,
  },
  itemTextChecked: {
    textDecorationLine: "line-through",
    opacity: 0.5,
  },
});
