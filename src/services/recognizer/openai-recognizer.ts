import OpenAI from "openai";
import type { Recognizer } from "./recognizer";

export class OpenAIRecognizer implements Recognizer {
  private client: OpenAI;
  private model: string;

  constructor(model: string, baseUrl: string | null, apiKey: string = "") {
    this.client = new OpenAI({
      baseURL: baseUrl,
      apiKey: apiKey,
      dangerouslyAllowBrowser: true,
    });
    this.model = model;
  }

  async recognize(blob: Blob): Promise<string> {
    const file = new File([blob], "audio.ogg", {
      type: blob.type,
      lastModified: Date.now(),
    });

    const transcription = await this.client.audio.transcriptions.create({
      file: file,
      model: this.model,
    });

    return transcription.text;
  }
}
