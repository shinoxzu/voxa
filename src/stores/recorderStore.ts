import { ref } from "vue";
import { defineStore } from "pinia";
import { WebApiRecorder } from "@/services/recorder/webapi-recorder";
import type { Recorder } from "@/services/recorder/recorder";

const recorder: Recorder = new WebApiRecorder();

export const useRecorderStore = defineStore("recorder", () => {
  const isRecording = ref(false);

  async function startRecording(callback: (blob: Blob) => void) {
    isRecording.value = true;
    await recorder.startRecording(callback);
  }

  async function stopRecording() {
    isRecording.value = false;
    await recorder.stopRecording();
  }

  return {
    startRecording,
    stopRecording,
    isRecording,
  };
});
