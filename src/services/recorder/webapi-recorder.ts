import type { Recorder } from "./recorder";

export class WebApiRecorder implements Recorder {
  private recorder: MediaRecorder | null = null;
  private currentChunks: Blob[] = [];

  async startRecording(callback: (blob: Blob) => void) {
    const displayStream = await navigator.mediaDevices.getDisplayMedia({
      video: true,
      audio: true,
    });
    const micStream = await navigator.mediaDevices.getUserMedia({
      audio: true,
    });

    const audioContext = new AudioContext();
    const destination = audioContext.createMediaStreamDestination();

    audioContext.createMediaStreamSource(displayStream).connect(destination);
    audioContext.createMediaStreamSource(micStream).connect(destination);

    const finalStream = new MediaStream(destination.stream.getAudioTracks());

    this.recorder = new MediaRecorder(finalStream);
    this.currentChunks = [];

    this.recorder.ondataavailable = (e) => this.currentChunks.push(e.data);
    this.recorder.start();

    this.recorder.onstop = () => {
      const blob = new Blob(this.currentChunks, { type: "audio/ogg" });

      this.recorder = null;
      this.currentChunks = [];

      callback(blob);
    };
  }

  stopRecording() {
    this.recorder?.stop();
  }
}
