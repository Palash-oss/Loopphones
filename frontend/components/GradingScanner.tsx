
import React, { useState, useRef, useCallback } from 'react';
import { Camera, RefreshCw, CheckCircle2, AlertCircle, Scan, ShieldCheck } from 'lucide-react';
import apiService from '../services/apiService';

interface GradingResult {
  grade: string;
  confidence: number;
  defects: string[];
  suggestedAction: string;
  estimatedValue: number;
}

export const GradingScanner: React.FC = () => {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [result, setResult] = useState<GradingResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const startCamera = async () => {
    try {
      const s = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      setStream(s);
      if (videoRef.current) {
        videoRef.current.srcObject = s;
      }
      setError(null);
    } catch (err) {
      setError("Camera permission denied or not available.");
    }
  };

  const stopCamera = () => {
    stream?.getTracks().forEach(track => track.stop());
    setStream(null);
  };

  const captureAndAnalyze = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current) return;

    setIsScanning(true);
    setResult(null);

    const canvas = canvasRef.current;
    const video = videoRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(video, 0, 0);
      const dataUrl = canvas.toDataURL('image/jpeg');
      
      try {
        const gradingResult = await apiService.gradeDevice({
          device_id: 'LP-99X-2026-ALPHA',
          image_urls: [dataUrl]
        });
        
        if (gradingResult?.grading) {
          setResult({
            grade: gradingResult.grading.grade || 'Good',
            confidence: gradingResult.grading.confidence || 0.85,
            defects: gradingResult.grading.defects || [],
            suggestedAction: gradingResult.grading.suggested_action || 'Resell',
            estimatedValue: gradingResult.price_estimate?.estimated_price || 980
          });
        }
        stopCamera();
      } catch (err) {
        setError("Backend grading failed. Ensure backend is running on port 8000.");
        console.error('Grading error:', err);
      } finally {
        setIsScanning(false);
      }
    }
  }, [stream]);

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold gradient-text">Automated Grading</h2>
        <p className="text-gray-400">Computer Vision powered cosmetic assessment</p>
      </div>

      {!stream && !result && (
        <div className="glass aspect-video rounded-3xl flex flex-col items-center justify-center p-8 border-dashed border-2 border-white/10">
          <div className="p-4 bg-emerald-500/10 rounded-full mb-4">
            <Camera className="text-emerald-400" size={48} />
          </div>
          <h3 className="text-xl font-semibold mb-2">Initialize Scanner</h3>
          <p className="text-gray-400 text-center mb-6">
            Place the device on a flat surface with good lighting for accurate ML analysis.
          </p>
          <button 
            onClick={startCamera}
            className="bg-emerald-500 hover:bg-emerald-400 text-black px-8 py-3 rounded-2xl font-bold flex items-center gap-2 transition-all shadow-lg shadow-emerald-500/20"
          >
            <Scan size={20} />
            Start Grading
          </button>
        </div>
      )}

      {stream && (
        <div className="relative group">
          <div className="glass rounded-3xl overflow-hidden aspect-video relative gradient-border">
            <video 
              ref={videoRef} 
              autoPlay 
              playsInline 
              className="w-full h-full object-cover grayscale-[20%]"
            />
            {/* HUD Overlay */}
            <div className="absolute inset-0 pointer-events-none border-[40px] border-black/20">
              <div className="w-full h-full border-2 border-emerald-500/30 rounded-xl relative">
                <div className="absolute top-0 left-0 w-8 h-8 border-t-4 border-l-4 border-emerald-500"></div>
                <div className="absolute top-0 right-0 w-8 h-8 border-t-4 border-r-4 border-emerald-500"></div>
                <div className="absolute bottom-0 left-0 w-8 h-8 border-b-4 border-l-4 border-emerald-500"></div>
                <div className="absolute bottom-0 right-0 w-8 h-8 border-b-4 border-r-4 border-emerald-500"></div>
                
                {/* Scanning animation line */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-[90%] h-[1px] bg-emerald-500/50 animate-bounce"></div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-4">
            <button 
              onClick={captureAndAnalyze}
              disabled={isScanning}
              className="bg-white text-black px-6 py-3 rounded-2xl font-bold flex items-center gap-2 hover:scale-105 transition-transform disabled:opacity-50"
            >
              {isScanning ? <RefreshCw className="animate-spin" /> : <Scan />}
              {isScanning ? 'Analyzing...' : 'Analyze Condition'}
            </button>
            <button 
              onClick={stopCamera}
              className="glass px-6 py-3 rounded-2xl font-bold flex items-center gap-2 hover:bg-white/10"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {result && (
        <div className="animate-in zoom-in-95 duration-300">
          <div className="glass p-8 rounded-3xl border-emerald-500/30 border">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-emerald-500/10 rounded-lg">
                  <ShieldCheck className="text-emerald-400" size={24} />
                </div>
                <div>
                  <h3 className="font-bold text-xl uppercase tracking-tighter">Certified Grade</h3>
                  <p className="text-gray-400 text-sm">ML Confidence: {(result.confidence * 100).toFixed(1)}%</p>
                </div>
              </div>
              <div className="text-4xl font-black text-emerald-400">{result.grade}</div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div>
                <span className="text-xs text-gray-400 uppercase font-bold tracking-widest">Detected Defects</span>
                <ul className="mt-2 space-y-2">
                  {result.defects.map((defect, i) => (
                    <li key={i} className="flex items-center gap-2 text-sm text-gray-300">
                      <div className="w-1.5 h-1.5 bg-yellow-500 rounded-full"></div>
                      {defect}
                    </li>
                  ))}
                  {result.defects.length === 0 && (
                    <li className="text-sm text-gray-500 italic">No cosmetic defects detected.</li>
                  )}
                </ul>
              </div>
              <div>
                <span className="text-xs text-gray-400 uppercase font-bold tracking-widest">Pricing & Logistics</span>
                <div className="mt-2 p-4 bg-white/5 rounded-2xl">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-400">Market Estimate</span>
                    <span className="font-bold text-lg">${result.estimatedValue}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-400">Queue Sorting</span>
                    <span className="text-xs bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded font-bold">{result.suggestedAction}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex gap-4">
              <button 
                onClick={() => { setResult(null); startCamera(); }}
                className="flex-1 glass py-4 rounded-2xl font-bold hover:bg-white/10 transition-colors"
              >
                Scan Again
              </button>
              <button className="flex-1 bg-emerald-500 text-black py-4 rounded-2xl font-bold hover:bg-emerald-400 transition-colors">
                Sync to Product Passport
              </button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-2xl flex items-center gap-3 text-red-400">
          <AlertCircle size={20} />
          <p className="text-sm">{error}</p>
        </div>
      )}

      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
};
