import { ref } from "vue";
import { defineStore } from "pinia";
import { OPENAI_SUMMARIZE_MODEL, OPENAI_BASE_SUMMARIZE_URL } from "@/config";
import { OpenAISummarizer } from "@/services/summarizer/openai-summarizer";
import type { Summarizer } from "@/services/summarizer/summarizer";

const summarizer: Summarizer = new OpenAISummarizer(
  OPENAI_SUMMARIZE_MODEL,
  OPENAI_BASE_SUMMARIZE_URL,
);

export const useSummarizerStore = defineStore("summarizer", () => {
  const isSummarizing = ref(false);

  async function summarize(text: string): Promise<string> {
    isSummarizing.value = true;

    try {
      return await summarizer.summarize(text);
    } finally {
      isSummarizing.value = false;
    }
  }

  return {
    summarize,
    isSummarizing,
  };
});
