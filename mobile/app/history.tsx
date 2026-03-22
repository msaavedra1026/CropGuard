import { useEffect } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  Image,
  StyleSheet,
  Dimensions,
} from "react-native";
import { useRouter } from "expo-router";
import { useScanStore } from "../stores/scanStore";
import { BACKEND_URL } from "../constants/api";
import { colors, fonts } from "../constants/theme";

const { width } = Dimensions.get("window");
const CARD_WIDTH = (width - 48) / 2;

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function HistoryScreen() {
  const router = useRouter();
  const { scanHistory, loadHistory } = useScanStore();

  useEffect(() => {
    loadHistory();
  }, []);

  const renderItem = ({ item }: { item: (typeof scanHistory)[0] }) => {
    const severityColor =
      colors.severity[item.severity as keyof typeof colors.severity] ?? colors.text2;

    return (
      <TouchableOpacity
        style={styles.card}
        onPress={() => router.push({ pathname: "/result", params: { scan_id: item.scan_id } })}
      >
        <Image
          source={{ uri: `${BACKEND_URL}${item.thumbnail_url}` }}
          style={styles.thumb}
          resizeMode="cover"
        />
        <View style={styles.cardBody}>
          <Text style={styles.diseaseName} numberOfLines={1}>
            {item.disease_name}
          </Text>
          <View style={[styles.badge, { backgroundColor: severityColor }]}>
            <Text style={styles.badgeText}>{item.severity}</Text>
          </View>
          <Text style={styles.timestamp}>{timeAgo(item.timestamp)}</Text>
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      {scanHistory.length === 0 ? (
        <View style={styles.empty}>
          <Text style={styles.emptyText}>No scans yet. Point your camera at a plant!</Text>
        </View>
      ) : (
        <FlatList
          data={scanHistory}
          keyExtractor={(item) => item.scan_id}
          renderItem={renderItem}
          numColumns={2}
          columnWrapperStyle={styles.row}
          contentContainerStyle={styles.list}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  list: { padding: 16 },
  row: { justifyContent: "space-between", marginBottom: 16 },
  card: {
    width: CARD_WIDTH,
    backgroundColor: colors.surface,
    borderRadius: 12,
    overflow: "hidden",
  },
  thumb: { width: "100%", height: CARD_WIDTH * 0.75 },
  cardBody: { padding: 10 },
  diseaseName: {
    fontFamily: fonts.headerFamily,
    fontSize: 14,
    color: colors.text1,
    marginBottom: 6,
  },
  badge: {
    alignSelf: "flex-start",
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 10,
    marginBottom: 6,
  },
  badgeText: {
    fontFamily: fonts.bodyMedium,
    fontSize: 11,
    color: colors.text1,
  },
  timestamp: {
    fontFamily: fonts.bodyFamily,
    fontSize: 12,
    color: colors.text2,
  },
  empty: { flex: 1, justifyContent: "center", alignItems: "center", padding: 40 },
  emptyText: {
    fontFamily: fonts.bodyFamily,
    fontSize: 16,
    color: colors.text2,
    textAlign: "center",
  },
});
