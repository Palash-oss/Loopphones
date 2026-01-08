
export enum DeviceGrade {
  MINT = 'Mint',
  EXCELLENT = 'Excellent',
  GOOD = 'Good',
  FAIR = 'Fair',
  RECYCLE = 'Recycle'
}

export interface TelemetryData {
  timestamp: string;
  batteryHealth: number;
  thermalEfficiency: number;
  marketValue: number;
}

export interface Device {
  id: string;
  model: string;
  serialNumber: string;
  passportId: string;
  currentGrade: DeviceGrade;
  currentValue: number;
  predictedValueDropDate: string;
  carbonOffset: number;
  repairHistory: RepairRecord[];
}

export interface RepairRecord {
  date: string;
  component: string;
  technician: string;
  impactOnValue: number;
}

export type ViewState = 'dashboard' | 'scanner' | 'passport' | 'marketplace' | 'logistics';
