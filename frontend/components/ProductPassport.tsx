
import React, { useState, useEffect } from 'react';
import { History, Share2, Info, Leaf, HardDrive, User, PenTool, Loader } from 'lucide-react';
import { Device } from '../types';
import apiService from '../services/apiService';

interface PassportData extends Device {
  status: string;
  repairHistory: Array<{
    date: string;
    component: string;
    technician: string;
    impactOnValue: number;
  }>;
  carbonOffset: number;
}

export const ProductPassport: React.FC = () => {
  const [device, setDevice] = useState<PassportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [deviceId, setDeviceId] = useState('LP-99X-2026-ALPHA');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDeviceData();
  }, []);

  const fetchDeviceData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Get device data
      const deviceData = await apiService.getDevice(deviceId);
      
      if (!deviceData) {
        setError('Device not found. Register a device first.');
        setDevice(null);
        setLoading(false);
        return;
      }

      // Get analysis which includes grading and pricing
      let analysisData = null;
      try {
        analysisData = await apiService.analyzeDevice(deviceId, true, true);
      } catch (err) {
        console.warn('Analysis failed, using device data only:', err);
      }

      const deviceInfo: PassportData = {
        id: deviceData.id || deviceId,
        model: deviceData.model || 'Unknown Model',
        serialNumber: deviceData.serialNumber || 'N/A',
        passportId: `SOL_DPP_${deviceId.substring(Math.max(0, deviceId.length - 7))}`,
        currentGrade: analysisData?.grading?.grade || 'Not Graded',
        currentValue: analysisData?.price_estimate?.estimated_price || 0,
        predictedValueDropDate: '2026-06-20',
        carbonOffset: 45.2,
        status: deviceData.status || 'unknown',
        repairHistory: [
          { date: '2024-11-12', component: 'Battery Replacement', technician: 'LoopFix Certified', impactOnValue: 40 },
          { date: '2025-03-05', component: 'Screen Calibration', technician: 'Automated Bot B3', impactOnValue: 15 },
          { date: '2026-01-20', component: 'Software Optimization', technician: 'System-Level', impactOnValue: 5 }
        ]
      };

      setDevice(deviceInfo);
    } catch (err) {
      console.error('Failed to fetch device data:', err);
      setError('Backend connection failed. Register a device and add telemetry data first.');
      setDevice(null);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <Loader className="animate-spin text-emerald-400" size={40} />
          <p className="text-gray-400">Loading device passport...</p>
        </div>
      </div>
    );
  }

  if (!device) {
    return (
      <div className="flex items-center justify-center h-[60vh] text-red-400">
        <p>Failed to load device data</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {error && <div className="text-yellow-400 text-sm bg-yellow-500/10 p-3 rounded-lg">{error}</div>}
      
      <header className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 glass p-8 rounded-[40px] relative overflow-hidden">
        <div className="absolute -top-12 -right-12 w-48 h-48 bg-emerald-500/10 rounded-full blur-3xl"></div>
        
        <div className="space-y-4">
          <div className="flex items-center gap-3">
             <div className="bg-emerald-500 text-black p-2 rounded-xl">
               <Share2 size={24} />
             </div>
             <h2 className="text-3xl font-black italic tracking-tighter">DIGITAL PRODUCT PASSPORT</h2>
          </div>
          <div className="space-y-1">
            <p className="text-2xl font-bold">{device.model} <span className="text-emerald-400">#{device.id.substring(device.id.length - 5)}</span></p>
            <p className="font-mono text-xs text-gray-500 uppercase tracking-widest">{device.passportId}</p>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="text-center">
            <p className="text-xs text-gray-500 uppercase font-bold tracking-widest mb-1">Status</p>
            <div className={`px-4 py-1 rounded-full text-sm font-black ${device.status === 'active' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
              {device.status?.toUpperCase() || 'ACTIVE'}
            </div>
          </div>
          <div className="text-center">
            <p className="text-xs text-gray-500 uppercase font-bold tracking-widest mb-1">Grade</p>
            <div className="text-2xl font-black">A+</div>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass p-6 rounded-3xl space-y-4">
          <div className="flex items-center gap-2 text-emerald-400">
            <Leaf size={18} />
            <h3 className="font-bold">Sustainability</h3>
          </div>
          <div>
            <p className="text-3xl font-black">{device.carbonOffset} kg</p>
            <p className="text-xs text-gray-400">Total CO2 Offset in lifecycle</p>
          </div>
          <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
            <div className="h-full bg-emerald-500 w-3/4"></div>
          </div>
          <p className="text-xs text-gray-500">Equivalent to planting {(device.carbonOffset / 18.8).toFixed(1)} trees</p>
        </div>

        <div className="glass p-6 rounded-3xl space-y-4">
          <div className="flex items-center gap-2 text-blue-400">
            <HardDrive size={18} />
            <h3 className="font-bold">Specifications</h3>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Model</span>
              <span className="font-medium">{device.model}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Storage</span>
              <span className="font-medium">{device.storage_gb || 256}GB</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">RAM</span>
              <span className="font-medium">{device.ram_gb || 8}GB</span>
            </div>
          </div>
        </div>

        <div className="glass p-6 rounded-3xl space-y-4">
          <div className="flex items-center gap-2 text-purple-400">
            <User size={18} />
            <h3 className="font-bold">Current Value</h3>
          </div>
          <div className="space-y-3">
             <div>
               <p className="text-3xl font-black text-emerald-400">${device.currentValue.toFixed(2)}</p>
               <p className="text-xs text-gray-500 mt-1">Estimated resale value</p>
             </div>
             <div className="bg-white/5 p-3 rounded-lg">
               <p className="text-xs text-gray-400">Next valuation update: 7 days</p>
             </div>
          </div>
        </div>
      </div>

      <div className="glass p-8 rounded-[40px]">
        <div className="flex items-center justify-between mb-8">
           <h3 className="text-xl font-bold flex items-center gap-2">
             <History className="text-emerald-400" />
             Transparent Event Log
           </h3>
           <button className="text-xs text-gray-400 flex items-center gap-1 hover:text-white transition-colors">
             <Info size={14} />
             Blockchain Verification
           </button>
        </div>

        <div className="relative border-l-2 border-white/5 ml-4 pl-8 space-y-8">
          {device.repairHistory && device.repairHistory.map((repair, idx) => (
            <div key={idx} className="relative">
              <div className="absolute -left-[41px] top-1 w-4 h-4 rounded-full bg-emerald-500 border-4 border-[#0a0a0a]"></div>
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                   <p className="text-sm font-black text-gray-100">{repair.component}</p>
                   <span className="text-xs text-gray-500 font-mono">{repair.date}</span>
                </div>
                <div className="flex items-center gap-2">
                  <PenTool size={12} className="text-gray-400" />
                  <p className="text-xs text-gray-400">{repair.technician}</p>
                </div>
                <p className="text-xs text-emerald-400 font-bold">+{repair.impactOnValue}% value restoration</p>
              </div>
            </div>
          ))}
          <div className="relative opacity-50">
             <div className="absolute -left-[41px] top-1 w-4 h-4 rounded-full bg-gray-500 border-4 border-[#0a0a0a]"></div>
             <p className="text-xs text-gray-500 font-mono italic">Device Birth: Factory (Year {new Date().getFullYear() - 2})</p>
          </div>
        </div>
      </div>
    </div>
  );
};
