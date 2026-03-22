import { create } from "zustand";
import { BACKEND_URL } from "../constants/api";

export interface ScanResult {
  scan_id: string;
  crop_type: string;
  disease: {
    name: string;
    confidence: number;
    severity: string;
    affected_percent: number;
    description: string;
    spread_risk?: string;
  };
  mask_url: string;
  nutrients: {
    deficiencies: string[];
    recommendations: {
      nutrient: string;
      symptom: string;
      treatment: string;
      frequency: string;
      organic_option: string;
    }[];
  };
  watering: {
    current_status: string;
    schedule: string;
    amount_ml_per_plant: number;
    warning: string | null;
  };
  pests: {
    detected: boolean;
    type: string | null;
    severity: string | null;
    treatment: string | null;
  };
  soil: {
    recommended_ph: string;
    amendments: string[];
    drainage: string;
  };
  care_plan: {
    immediate: string[];
    this_week: string[];
    ongoing: string[];
  };
  recovery_outlook: string;
}

export interface ScanSummary {
  scan_id: string;
  timestamp: string;
  crop_type: string;
  disease_name: string;
  severity: string;
  thumbnail_url: string;
}

interface ScanStore {
  currentScanId: string | null;
  currentResult: ScanResult | null;
  scanHistory: ScanSummary[];
  isAnalyzing: boolean;
  error: string | null;
  startAnalysis: (imageUri: string) => Promise<void>;
  setResult: (result: ScanResult) => void;
  loadHistory: () => Promise<void>;
  clearCurrent: () => void;
}

export const useScanStore = create<ScanStore>((set) => ({
  currentScanId: null,
  currentResult: null,
  scanHistory: [],
  isAnalyzing: false,
  error: null,

  startAnalysis: async (imageUri: string) => {
    set({ isAnalyzing: true, error: null, currentResult: null });
    try {
      const formData = new FormData();
      const filename = imageUri.split("/").pop() || "photo.jpg";
      formData.append("image", {
        uri: imageUri,
        name: filename,
        type: "image/jpeg",
      } as any);

      const response = await fetch(`${BACKEND_URL}/analyze`, {
        method: "POST",
        body: formData,
        headers: { "Content-Type": "multipart/form-data" },
      });

      if (!response.ok) throw new Error(`Server error: ${response.status}`);
      const result: ScanResult = await response.json();
      set({ currentScanId: result.scan_id, currentResult: result, isAnalyzing: false });
    } catch (err: any) {
      set({ error: err.message || "Analysis failed", isAnalyzing: false });
    }
  },

  setResult: (result) => set({ currentResult: result, currentScanId: result.scan_id }),

  loadHistory: async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/history`);
      if (!response.ok) throw new Error(`Server error: ${response.status}`);
      const history: ScanSummary[] = await response.json();
      set({ scanHistory: history });
    } catch (err: any) {
      set({ error: err.message || "Failed to load history" });
    }
  },

  clearCurrent: () => set({ currentScanId: null, currentResult: null, error: null }),
}));
