export interface Recorder {
  startRecording(callback: (blob: Blob) => void): Promise<void>;

  stopRecording(): void;
}
