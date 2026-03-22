import { useEffect, useRef } from "react";
import { View, Image, Animated, StyleSheet, Dimensions } from "react-native";
import { BACKEND_URL } from "../constants/api";

const { width } = Dimensions.get("window");
const IMAGE_HEIGHT = width * 0.75;

interface Props {
  scanId: string;
}

export default function MaskOverlay({ scanId }: Props) {
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 600,
      useNativeDriver: true,
    }).start();
  }, []);

  return (
    <View style={styles.container}>
      {/* Original image - we use the mask endpoint as thumbnail for now */}
      <View style={styles.imageWrapper}>
        <Image
          source={{ uri: `${BACKEND_URL}/masks/${scanId}.png` }}
          style={styles.baseImage}
          resizeMode="cover"
        />
        {/* Mask overlay with orange-red tint */}
        <Animated.View style={[styles.maskLayer, { opacity: fadeAnim }]}>
          <Image
            source={{ uri: `${BACKEND_URL}/masks/${scanId}.png` }}
            style={[styles.baseImage, { tintColor: "#FF6B35" }]}
            resizeMode="cover"
          />
        </Animated.View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { width, height: IMAGE_HEIGHT },
  imageWrapper: { flex: 1, position: "relative" },
  baseImage: { width: "100%", height: "100%" },
  maskLayer: {
    ...StyleSheet.absoluteFillObject,
    opacity: 0.5,
  },
});
