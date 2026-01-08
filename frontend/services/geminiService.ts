
// Gemini service deprecated - all ML handled by backend
// Backend uses: YOLO for grading, TensorFlow for RUL, XGBoost for pricing

export interface GradingResult {
  grade: string;
  confidence: number;
  defects: string[];
  suggestedAction: string;
  estimatedValue: number;
}

export const analyzeDeviceGrading = async (imageBase64: string): Promise<GradingResult> => {
  throw new Error('Backend handles all ML analysis. Use apiService.gradeDevice() instead.');
};

export const getMarketPrediction = async (deviceModel: string, telemetry: any) => {
  throw new Error('Use apiService.analyzeDevice() instead for market predictions.');
