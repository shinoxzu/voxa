import { ref } from "vue";
import { defineStore } from "pinia";
import {
  OPENAI_RECOGNITION_MODEL,
  OPENAI_BASE_RECOGNITION_URL,
} from "@/config";
import { OpenAIRecognizer } from "@/services/recognizer/openai-recognizer";
import type { Recognizer } from "@/services/recognizer/recognizer";

const recognizer: Recognizer = new OpenAIRecognizer(
  OPENAI_RECOGNITION_MODEL,
  OPENAI_BASE_RECOGNITION_URL,
);

export const useRecognizerStore = defineStore("recognizer", () => {
  const isRecognizing = ref(false);

  async function recognize(blob: Blob): Promise<string> {
    isRecognizing.value = true;

    try {
      return await recognizer.recognize(blob);
    } finally {
      isRecognizing.value = false;
    }
  }

  return {
    recognize,
    isRecognizing,
  };
});
