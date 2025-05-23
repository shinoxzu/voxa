<script setup lang="ts">
import ProgressSpinner from "primevue/progressspinner";
import Button from "primevue/button";
import Toast from "primevue/toast";
import { useRecorderStore } from "@/stores/recorderStore";
import { useSummarizerStore } from "@/stores/summarizerStore";
import { useRecognizerStore } from "@/stores/recognizerStore";
import { ref, computed } from "vue";
import { useToast } from "primevue/usetoast";

const toast = useToast();
const recorderStore = useRecorderStore();
const recognizerStore = useRecognizerStore();
const summarizerStore = useSummarizerStore();

const recognizedText = ref<string | null>(null);
const summary = ref<string | null>(null);
const isProcessing = computed(
  () => recognizerStore.isRecognizing || summarizerStore.isSummarizing,
);

async function onRecordingStopped(blob: Blob) {
  try {
    recognizedText.value = await recognizerStore.recognize(blob);

    if (recognizedText.value) {
      summary.value = await summarizerStore.summarize(recognizedText.value);
    }
  } catch (err) {
    console.error("error when recognizing + summarizing", err);
    toast.add({
      severity: "error",
      summary: "Ошибка",
      detail: "Произошла ошибка при обработке аудио",
      life: 3000,
    });
  }
}

async function startRecording() {
  try {
    clearLastSummarizeResults();
    await recorderStore.startRecording(onRecordingStopped);
  } catch (err) {
    console.error("error when starting recording", err);
    toast.add({
      severity: "error",
      summary: "Ошибка",
      detail: "Не удалось начать запись",
      life: 3000,
    });
  }
}

function stopRecording() {
  recorderStore.stopRecording();
}

function copyToClipboard(text: string) {
  navigator.clipboard
    .writeText(text)
    .then(() => {
      toast.add({
        severity: "success",
        summary: "Успех",
        detail: "Текст скопирован в буфер обмена",
        life: 2000,
      });
    })
    .catch(() => {
      toast.add({
        severity: "error",
        summary: "Ошибка",
        detail: "Не удалось скопировать текст",
        life: 3000,
      });
    });
}

function clearLastSummarizeResults() {
  recognizedText.value = null;
  summary.value = null;
}
</script>

<template>
  <Toast />

  <div class="container">
    <h1>Подведение итогов конференции</h1>

    <div class="status-container">
      <div v-if="recorderStore.isRecording" class="status-block">
        <ProgressSpinner />
      </div>

      <div v-if="recognizerStore.isRecognizing" class="status-block">
        <ProgressSpinner />
        <h3>Идет распознавание...</h3>
      </div>

      <div v-if="summarizerStore.isSummarizing" class="status-block">
        <ProgressSpinner />
        <h3>Идет подведение итогов...</h3>
      </div>
    </div>

    <div class="controls">
      <Button
        label="Начать запись"
        icon="pi pi-microphone"
        severity="primary"
        v-if="!recorderStore.isRecording && !isProcessing"
        @click="startRecording"
      />

      <Button
        label="Остановить запись"
        icon="pi pi-stop-circle"
        severity="danger"
        v-if="recorderStore.isRecording"
        @click="stopRecording"
      />
    </div>

    <div v-if="summary" class="result-container">
      <div class="result-card">
        <h2>Итоги конференции</h2>
        <div class="text-content">
          <p>{{ summary }}</p>
        </div>
        <div class="result-actions">
          <Button
            icon="pi pi-copy"
            severity="secondary"
            @click="copyToClipboard(summary)"
            label="Копировать итоги"
          />
        </div>
      </div>
    </div>

    <div v-if="recognizedText" class="result-container">
      <div class="result-card">
        <h2>Расшифровка</h2>
        <div class="text-content">
          <p>{{ recognizedText }}</p>
        </div>
        <div class="result-actions">
          <Button
            icon="pi pi-copy"
            severity="secondary"
            @click="copyToClipboard(recognizedText)"
            label="Копировать расшифровку"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
}

.status-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.status-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px 25px;
  background-color: var(--p-surface-900);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 300px;
}

.controls {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 30px;
}

.result-container {
  margin-top: 30px;
}

.result-card {
  background-color: var(--p-surface-900);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.text-content {
  margin: 15px 0;
  padding: 15px;
  border-radius: 6px;
  line-height: 1.6;
}

.result-actions {
  display: flex;
  justify-content: flex-end;
}
</style>
