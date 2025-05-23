import OpenAI from "openai";
import type { Summarizer } from "./summarizer";

export class OpenAISummarizer implements Summarizer {
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

  async summarize(text: string): Promise<string> {
    const response = await this.client.chat.completions.create({
      model: this.model,
      messages: [
        {
          role: "system",
          content:
            "You are a text summarizer. Summarize provided text for 200~ symbols. Answer only with summarize on provided language.",
        },
        { role: "user", content: text },
      ],
    });

    return response.choices[0].message.content || "—";
  }
}
