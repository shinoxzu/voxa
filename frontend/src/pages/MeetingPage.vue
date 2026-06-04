<script setup lang="ts">
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import InputText from "primevue/inputtext";
import ProgressBar from "primevue/progressbar";
import Toast from "primevue/toast";
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useToast } from "primevue/usetoast";
import { useMeetingStore } from "@/stores/meetingStore";
import { api, type ActionItem } from "@/services/api";

const props = defineProps<{ id: string }>();
const toast = useToast();
const store = useMeetingStore();

const issueDialog = ref(false);
const selectedItem = ref<ActionItem | null>(null);
const issueQueue = ref("VOXA");
const isCreatingIssue = ref(false);

const isProcessing = computed(() => store.currentMeeting?.status === "processing");
const isDone = computed(() => store.currentMeeting?.status === "done");

const progressValue = computed(() => {
  const steps = store.processingStatus?.steps;
  if (!steps) return 0;
  let done = 0;
  if (steps.transcription === "done") done++;
  if (steps.diarization === "done") done++;
  if (steps.analysis === "done") done++;
  return Math.round((done / 3) * 100);
});

const stepLabel = computed(() => {
  const step = store.processingStatus?.step;
  if (step === "transcription") return "Транскрипция...";
  if (step === "diarization") return "Разделение спикеров...";
  if (step === "analysis") return "Анализ и суммаризация...";
  return "Обработка...";
});

onMounted(async () => {
  await store.fetchMeeting(props.id);
  if (store.currentMeeting?.status === "processing") {
    store.startPolling(props.id);
  }
});

onUnmounted(() => {
  store.clearCurrent();
});

function openIssueDialog(item: ActionItem) {
  selectedItem.value = item;
  issueDialog.value = true;
}

async function confirmCreateIssue() {
  if (!selectedItem.value || isCreatingIssue.value) return;
  isCreatingIssue.value = true;
  try {
    const issue = await api.createIssue(props.id, selectedItem.value.id, {
      summary: selectedItem.value.task,
      assignee: selectedItem.value.assignee,
      deadline: selectedItem.value.deadline ?? undefined,
      queue: issueQueue.value,
    });
    toast.add({
      severity: "success",
      summary: "Задача создана",
      detail: issue.key,
      life: 3000,
    });
    issueDialog.value = false;
    await store.fetchMeeting(props.id);
  } catch {
    toast.add({
      severity: "error",
      summary: "Ошибка",
      detail: "Не удалось создать задачу",
      life: 3000,
    });
  } finally {
    isCreatingIssue.value = false;
  }
}

function formatTime(sec: number): string {
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function copyToClipboard(text: string) {
  navigator.clipboard.writeText(text).then(() => {
    toast.add({ severity: "success", summary: "Скопировано", life: 1500 });
  });
}
</script>

<template>
  <Toast />
  <div class="container">
    <h1>{{ store.currentMeeting?.title ?? "Загрузка..." }}</h1>

    <div v-if="isProcessing" class="processing-card">
      <p>{{ stepLabel }}</p>
      <ProgressBar :value="progressValue" />
    </div>

    <div v-if="store.currentMeeting?.status === 'error'" class="error-card">
      <p>Произошла ошибка при обработке встречи.</p>
    </div>

    <template v-if="isDone">
      <div class="result-card">
        <div class="card-header">
          <h2>Резюме</h2>
          <Button
            v-if="store.currentMeeting?.summary"
            icon="pi pi-copy"
            severity="secondary"
            text
            @click="copyToClipboard(store.currentMeeting!.summary!)"
          />
        </div>
        <p class="summary-text">{{ store.currentMeeting?.summary }}</p>
      </div>

      <div v-if="store.currentMeeting?.action_items?.length" class="result-card">
        <h2>Задачи</h2>
        <div class="action-items">
          <div v-for="item in store.currentMeeting.action_items" :key="item.id" class="action-item">
            <div class="action-content">
              <span class="speaker-tag">{{ item.assignee }}</span>
              <span>{{ item.task }}</span>
              <span v-if="item.deadline" class="deadline">до {{ item.deadline }}</span>
            </div>
            <div class="action-controls">
              <a
                v-if="item.tracker_issue"
                :href="item.tracker_issue.url"
                target="_blank"
                class="issue-link"
              >
                {{ item.tracker_issue.key }}
              </a>
              <Button
                v-else
                label="Создать в трекере"
                icon="pi pi-external-link"
                severity="secondary"
                size="small"
                @click="openIssueDialog(item)"
              />
            </div>
          </div>
        </div>
      </div>

      <div class="result-card">
        <div class="card-header">
          <h2>Транскрипт</h2>
          <Button
            v-if="store.currentMeeting?.transcript"
            icon="pi pi-copy"
            severity="secondary"
            text
            @click="
              copyToClipboard(
                store.currentMeeting!.transcript!.map(
                  (s) => `${s.speaker}: ${s.text}`,
                ).join('\n'),
              )
            "
          />
        </div>
        <div class="transcript">
          <div v-for="(seg, i) in store.currentMeeting?.transcript" :key="i" class="transcript-seg">
            <span class="seg-time">{{ formatTime(seg.start) }}</span>
            <span class="speaker-tag">{{ seg.speaker }}</span>
            <span>{{ seg.text }}</span>
          </div>
        </div>
      </div>
    </template>

    <Dialog v-model:visible="issueDialog" header="Создать задачу в трекере" modal style="width: 400px">
      <div class="dialog-content">
        <label>Очередь</label>
        <InputText v-model="issueQueue" class="full-width" />
        <label>Задача</label>
        <InputText :model-value="selectedItem?.task" disabled class="full-width" />
      </div>
      <template #footer>
        <Button label="Отмена" severity="secondary" @click="issueDialog = false" />
        <Button label="Создать" :loading="isCreatingIssue" @click="confirmCreateIssue" />
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  margin-bottom: 24px;
}

.processing-card,
.error-card {
  background: var(--p-content-background);
  border: 1px solid var(--p-content-border-color);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 20px;
}

.error-card {
  border-color: var(--p-red-500);
}

.result-card {
  background: var(--p-content-background);
  border: 1px solid var(--p-content-border-color);
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  padding: 20px;
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

h2 {
  font-size: 1.1rem;
  margin-bottom: 12px;
}

.summary-text {
  line-height: 1.6;
}

.action-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-radius: 6px;
  background: var(--p-content-hover-background);
  gap: 12px;
}

.action-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.action-controls {
  flex-shrink: 0;
}

.speaker-tag {
  background: var(--p-primary-color);
  color: var(--p-primary-contrast-color);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap;
}

.deadline {
  opacity: 0.6;
  font-size: 0.9rem;
}

.issue-link {
  color: var(--p-primary-color);
  text-decoration: none;
  font-weight: 600;
}

.transcript {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 500px;
  overflow-y: auto;
}

.transcript-seg {
  display: flex;
  gap: 8px;
  align-items: baseline;
  line-height: 1.5;
}

.seg-time {
  font-size: 0.8rem;
  opacity: 0.5;
  font-family: monospace;
  flex-shrink: 0;
}

.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.full-width {
  width: 100%;
}
</style>
