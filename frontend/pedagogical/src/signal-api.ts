export type SignalPulseType = 'cw' | 'lfm';
export type ChirpDirection = 'up' | 'down';
export type EnvelopeModel = 'rectangular' | 'tukey';

export type SignalRequest = {
  pulse_type: SignalPulseType;
  center_frequency_khz: number;
  duration_ms: number;
  bandwidth_khz: number;
  chirp_direction: ChirpDirection;
  envelope_model: EnvelopeModel;
};

export type TraceSeries = {
  x: number[];
  y: number[];
  x_unit: string;
  y_unit: string;
};

export type SignalResponse = {
  pulse_type: SignalPulseType;
  waveform: TraceSeries;
  instantaneous_frequency: TraceSeries;
  matched_filter: TraceSeries;
  metadata: Record<string, number | string>;
};

const DEFAULT_API_BASE = 'http://127.0.0.1:8000';

export async function fetchSignalResponse(
  request: SignalRequest,
  signal?: AbortSignal,
): Promise<SignalResponse> {
  const base = (import.meta.env.VITE_HYDROSIM_API_BASE as string | undefined) ?? DEFAULT_API_BASE;
  const response = await fetch(`${base}/api/v1/pedagogical/signal`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(request),
    signal,
  });
  if (!response.ok) {
    throw new Error(`HydroSIM Signal API returned ${response.status}`);
  }
  return response.json() as Promise<SignalResponse>;
}
