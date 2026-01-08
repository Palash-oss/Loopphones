const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1';

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    const res = await fetch(url, config);
    
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
      throw new Error(error.detail || `HTTP ${res.status}`);
    }

    return res.json();
  }

  async getTelemetryHistory(deviceId: string, days: number = 30): Promise<any[]> {
    return this.request(`/telemetry/${deviceId}?days=${days}`);
  }

  async getDevice(deviceId: string): Promise<any> {
    return this.request(`/devices/${deviceId}`);
  }

  async listDevices(): Promise<any[]> {
    return this.request(`/devices`);
  }

  async registerDevice(device: any): Promise<any> {
    return this.request(`/devices`, {
      method: 'POST',
      body: JSON.stringify(device),
    });
  }

  async ingestTelemetry(data: any): Promise<any> {
    return this.request(`/telemetry`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async analyzeDevice(deviceId: string, includeGrading: boolean = true, includePricing: boolean = true, imageUrls?: string[]): Promise<any> {
    const params = new URLSearchParams({
      include_grading: includeGrading.toString(),
      include_pricing: includePricing.toString(),
    });

    const body = imageUrls ? { image_urls: imageUrls } : null;

    return this.request(`/analysis/${deviceId}?${params}`, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async gradeDevice(request: any): Promise<any> {
    return this.request(`/grading`, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getPassportByDevice(deviceId: string): Promise<any> {
    return this.request(`/passports/device/${deviceId}`);
  }

  async createPassport(deviceId: string, ownerAddress: string): Promise<any> {
    return this.request(`/passports`, {
      method: 'POST',
      body: JSON.stringify({ device_id: deviceId, owner_address: ownerAddress }),
    });
  }

  async getStats(): Promise<any> {
    return this.request(`/stats`);
  }

  async healthCheck(): Promise<any> {
    return fetch(`${this.baseUrl.replace('/api/v1', '')}/health`).then(r => {
      if (!r.ok) throw new Error(`Health check failed: ${r.status}`);
      return r.json();
    });
  }
}

export const apiService = new ApiService();
export default apiService;
