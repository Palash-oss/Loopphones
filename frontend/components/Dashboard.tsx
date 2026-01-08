
import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area 
} from 'recharts';
import { TrendingUp, Battery, Zap, DollarSign, AlertCircle, Loader } from 'lucide-react';
import { TelemetryData } from '../types';
import apiService from '../services/apiService';

interface ChartData {
  timestamp: string;
  batteryHealth: number;
  thermalEfficiency: number;
  marketValue: number;
}

export const Dashboard: React.FC = () => {
  const [telemetryData, setTelemetryData] = useState<ChartData[]>([]);
  const [metrics, setMetrics] = useState({
    batteryHealth: 0,
    thermalEfficiency: 0,
    marketValue: 0,
    circularYield: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deviceId, setDeviceId] = useState('LP-99X-2026-ALPHA');
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    fetchTelemetryData();
    checkConnection();
  }, []);

  const checkConnection = async () => {
    try {
      await apiService.healthCheck();
      setConnected(true);
    } catch (err) {
      setConnected(false);
      console.error('Connection check failed:', err);
    }
  };

  const fetchTelemetryData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch telemetry history
      const history = await apiService.getTelemetryHistory(deviceId, 30);
      
      if (!history || history.length === 0) {
        setError('No telemetry data available for this device. Scan or ingest data first.');
        setTelemetryData([]);
        setMetrics({
          batteryHealth: 0,
          thermalEfficiency: 0,
          marketValue: 0,
          circularYield: 0,
        });
        setLoading(false);
        return;
      }

      // Transform data for charts
      const chartData: ChartData[] = history.map((item: any, index: number) => ({
        timestamp: new Date(item.timestamp).toLocaleDateString('en-US', { month: 'short' }),
        batteryHealth: item.battery_health_percentage || 0,
        thermalEfficiency: 100 - (item.battery_temperature || 0) / 1.5,
        marketValue: 1200 - (index * 50),
      }));

      setTelemetryData(chartData);

      // Get latest metrics from most recent telemetry
      if (history.length > 0) {
        const latest = history[0];
        setMetrics({
          batteryHealth: latest.battery_health_percentage || 0,
          thermalEfficiency: 100 - (latest.battery_temperature || 0) / 1.5,
          marketValue: 1200 - (history.length * 50),
          circularYield: 12.4,
        });
      }
    } catch (err) {
      console.error('Failed to fetch telemetry:', err);
      setError('Backend connection failed. No telemetry data to display.');
      setTelemetryData([]);
      setMetrics({
        batteryHealth: 0,
        thermalEfficiency: 0,
        marketValue: 0,
        circularYield: 0,
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <Loader className="animate-spin text-emerald-400" size={40} />
          <p className="text-gray-400">Loading telemetry data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold gradient-text">Telemetry Insights</h1>
          <p className="text-gray-400">Device ID: {deviceId}</p>
          {error && <p className="text-yellow-400 text-sm mt-1">{error}</p>}
        </div>
        <div className="flex gap-2">
          <div className={`glass px-4 py-2 rounded-full flex items-center gap-2 ${connected ? 'border-green-500/20 border' : 'border-red-500/20 border'}`}>
            <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
            <span className="text-sm font-medium">{connected ? 'Live Connection' : 'Offline Mode'}</span>
          </div>
        </div>
      </header>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard 
          icon={<Battery className="text-green-400" />} 
          label="Battery Health" 
          value={`${metrics.batteryHealth.toFixed(1)}%`}
          change={`${metrics.batteryHealth < 95 ? '-' : '+'}${Math.abs(metrics.batteryHealth - 95).toFixed(1)}%`}
          status={metrics.batteryHealth > 80 ? 'good' : metrics.batteryHealth > 50 ? 'warning' : 'danger'}
        />
        <MetricCard 
          icon={<Zap className="text-yellow-400" />} 
          label="Thermal Efficiency" 
          value={`${metrics.thermalEfficiency.toFixed(1)}%`}
          change={metrics.thermalEfficiency > 90 ? 'Optimal Range' : 'Monitor'}
          status={metrics.thermalEfficiency > 80 ? 'good' : 'warning'}
        />
        <MetricCard 
          icon={<TrendingUp className="text-blue-400" />} 
          label="Buy-Back Value" 
          value={`$${metrics.marketValue.toFixed(2)}`}
          change={metrics.marketValue < 1000 ? '-7.5% drop alert' : 'Stable'}
          status={metrics.marketValue < 1000 ? 'warning' : 'good'}
        />
        <MetricCard 
          icon={<DollarSign className="text-emerald-400" />} 
          label="Circular Yield" 
          value={`${metrics.circularYield.toFixed(1)}x`}
          change="+1.2x lifecycle"
          status="good"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass p-6 rounded-3xl">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-semibold text-lg">Value Degradation Curve</h3>
            <span className="text-xs bg-white/5 px-2 py-1 rounded text-gray-400 uppercase tracking-wider font-bold">Market Prediction</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={telemetryData}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2dd4bf" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#2dd4bf" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="timestamp" stroke="#666" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#666" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
                  itemStyle={{ color: '#2dd4bf' }}
                />
                <Area type="monotone" dataKey="marketValue" stroke="#2dd4bf" fillOpacity={1} fill="url(#colorValue)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass p-6 rounded-3xl">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-semibold text-lg">Hardware Degradation (RUL)</h3>
            <span className="text-xs bg-white/5 px-2 py-1 rounded text-gray-400 uppercase tracking-wider font-bold">Telemetry</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={telemetryData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="timestamp" stroke="#666" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#666" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip 
                   contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
                />
                <Line type="monotone" dataKey="batteryHealth" stroke="#4ade80" strokeWidth={3} dot={{ r: 4, fill: '#4ade80' }} activeDot={{ r: 6 }} />
                <Line type="monotone" dataKey="thermalEfficiency" stroke="#facc15" strokeWidth={3} strokeDasharray="5 5" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="glass p-6 rounded-3xl border-l-4 border-yellow-500/50 flex items-start gap-4">
        <AlertCircle className="text-yellow-500 mt-1 flex-shrink-0" size={24} />
        <div>
          <h4 className="font-bold text-yellow-500">Predictive Buy-Back Alert</h4>
          <p className="text-gray-300 mt-1">
            Our ML model predicts a <span className="text-white font-bold">15% drop</span> in resale value for iPhone 15 Pro series devices in the next 14 days due to market saturation. Sell now to maximize your Circular yield.
          </p>
          <button className="mt-3 bg-yellow-500 text-black px-4 py-2 rounded-lg font-bold text-sm hover:bg-yellow-400 transition-colors">
            Initate Resale
          </button>
        </div>
      </div>
    </div>
  );
};

const MetricCard: React.FC<{ icon: React.ReactNode, label: string, value: string, change: string, status: 'good' | 'warning' | 'danger' }> = ({ icon, label, value, change, status }) => (
  <div className="glass p-5 rounded-2xl hover:bg-white/5 transition-all cursor-default">
    <div className="flex items-center gap-3 mb-3">
      <div className="p-2 bg-white/5 rounded-lg">{icon}</div>
      <span className="text-gray-400 text-sm font-medium">{label}</span>
    </div>
    <div className="text-2xl font-bold mb-1">{value}</div>
    <div className={`text-xs ${status === 'warning' ? 'text-yellow-400' : status === 'danger' ? 'text-red-400' : 'text-green-400'}`}>
      {change}
    </div>
  </div>
);
