import type { Recorder } from "./recorder";

export class WebApiRecorder implements Recorder {
  private recorder: MediaRecorder | null = null;
  private currentChunks: Blob[] = [];
  private streams: MediaStream[] = [];
  private audioContext: AudioContext | null = null;

  async startRecording(callback: (blob: Blob) => void) {
    const displayStream = await navigator.mediaDevices.getDisplayMedia({
      video: true,
      audio: true,
    });
    const micStream = await navigator.mediaDevices.getUserMedia({
      audio: true,
    });

    this.streams = [displayStream, micStream];
    this.audioContext = new AudioContext();
    const destination = this.audioContext.createMediaStreamDestination();

    this.audioContext.createMediaStreamSource(displayStream).connect(destination);
    this.audioContext.createMediaStreamSource(micStream).connect(destination);

    const finalStream = new MediaStream(destination.stream.getAudioTracks());

    this.recorder = new MediaRecorder(finalStream);
    this.currentChunks = [];

    this.recorder.ondataavailable = (e) => this.currentChunks.push(e.data);
    this.recorder.start();

    this.recorder.onstop = () => {
      const blob = new Blob(this.currentChunks, { type: "audio/ogg" });

      this.cleanup();
      callback(blob);
    };
  }

  stopRecording() {
    this.recorder?.stop();
  }

  private cleanup() {
    for (const stream of this.streams) {
      stream.getTracks().forEach((t) => t.stop());
    }
    this.streams = [];
    this.audioContext?.close();
    this.audioContext = null;
    this.recorder = null;
    this.currentChunks = [];
  }
}
