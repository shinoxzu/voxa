<script setup lang="ts">
import Button from "primevue/button";
import FileUpload, { type FileUploadSelectEvent } from "primevue/fileupload";
import InputText from "primevue/inputtext";
import ProgressSpinner from "primevue/progressspinner";
import Toast from "primevue/toast";
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "primevue/usetoast";
import { useRecorderStore } from "@/stores/recorderStore";
import { useMeetingStore } from "@/stores/meetingStore";

const router = useRouter();
const toast = useToast();
const recorderStore = useRecorderStore();
const meetingStore = useMeetingStore();

const title = ref("");
const selectedFile = ref<File | null>(null);

async function onRecordingStopped(blob: Blob) {
  try {
    const meetingTitle = title.value || `Встреча ${new Date().toLocaleString("ru")}`;
    const id = await meetingStore.uploadMeeting(blob, meetingTitle);
    router.push(`/meetings/${id}`);
  } catch {
    toast.add({
      severity: "error",
      summary: "Ошибка",
      detail: "Не удалось отправить запись",
      life: 3000,
    });
  }
}

async function startRecording() {
  try {
    await recorderStore.startRecording(onRecordingStopped);
  } catch {
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

function onFileSelect(event: FileUploadSelectEvent) {
  selectedFile.value = event.files[0];
}

async function uploadFile() {
  if (!selectedFile.value) return;
  try {
    const meetingTitle = title.value || selectedFile.value.name;
    const id = await meetingStore.uploadMeeting(selectedFile.value, meetingTitle);
    router.push(`/meetings/${id}`);
  } catch {
    toast.add({
      severity: "error",
      summary: "Ошибка",
      detail: "Не удалось загрузить файл",
      life: 3000,
    });
  }
}
</script>

<template>
  <Toast />
  <div class="container">
    <h1>Новая встреча</h1>

    <div class="input-row">
      <InputText v-model="title" placeholder="Название встречи (необязательно)" class="title-input" />
    </div>

    <div class="section">
      <h2>Записать из браузера</h2>
      <div class="controls">
        <div v-if="recorderStore.isRecording" class="recording-indicator">
          <ProgressSpinner style="width: 24px; height: 24px" />
          <span>Запись идёт...</span>
        </div>
        <Button
          v-if="!recorderStore.isRecording"
          label="Начать запись"
          icon="pi pi-microphone"
          severity="primary"
          @click="startRecording"
          :disabled="meetingStore.isUploading"
        />
        <Button
          v-if="recorderStore.isRecording"
          label="Остановить"
          icon="pi pi-stop-circle"
          severity="danger"
          @click="stopRecording"
        />
      </div>
    </div>

    <div class="divider">
      <span>или</span>
    </div>

    <div class="section">
      <h2>Загрузить файл</h2>
      <div class="upload-area">
        <FileUpload
          mode="basic"
          accept="audio/*,video/*"
          :auto="false"
          chooseLabel="Выбрать файл"
          @select="onFileSelect"
        />
        <Button
          v-if="selectedFile"
          :label="`Загрузить: ${selectedFile.name}`"
          icon="pi pi-upload"
          severity="primary"
          @click="uploadFile"
          :loading="meetingStore.isUploading"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
}

h2 {
  font-size: 1.1rem;
  margin-bottom: 12px;
  opacity: 0.8;
}

.input-row {
  margin-bottom: 30px;
}

.title-input {
  width: 100%;
}

.section {
  background: var(--p-surface-900);
  border-radius: 8px;
  padding: 20px;
}

.controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.recording-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 20px 0;
  opacity: 0.5;
}

.divider::before,
.divider::after {
  content: "";
  flex: 1;
  border-top: 1px solid var(--p-surface-600);
}

.upload-area {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
