export interface Recognizer {
  recognize(blob: Blob): Promise<string>;
}
