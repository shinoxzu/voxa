<script setup lang="ts">
import Button from "primevue/button";
import { useConfirm } from "primevue/useconfirm";
import ConfirmDialog from "primevue/confirmdialog";
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { useMeetingStore } from "@/stores/meetingStore";

const router = useRouter();
const store = useMeetingStore();
const confirm = useConfirm();

onMounted(() => {
  store.fetchMeetings();
});

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString("ru");
}

function statusLabel(status: string): string {
  if (status === "done") return "Готово";
  if (status === "processing") return "Обработка...";
  return "Ошибка";
}

function onDelete(id: string) {
  confirm.require({
    message: "Удалить встречу? Это действие необратимо.",
    header: "Подтверждение",
    acceptLabel: "Удалить",
    rejectLabel: "Отмена",
    acceptClass: "p-button-danger",
    accept: () => store.deleteMeeting(id),
  });
}
</script>

<template>
  <ConfirmDialog />
  <div class="container">
    <h1>История встреч</h1>

    <div v-if="!store.meetings.length" class="empty">
      <p>Встреч пока нет</p>
      <Button label="Создать первую" icon="pi pi-plus" @click="router.push('/')" />
    </div>

    <div v-else class="meetings-list">
      <div
        v-for="m in store.meetings"
        :key="m.id"
        class="meeting-row"
        @click="router.push(`/meetings/${m.id}`)"
      >
        <div class="meeting-info">
          <span class="meeting-title">{{ m.title }}</span>
          <span class="meeting-date">{{ formatDate(m.created_at) }}</span>
        </div>
        <div class="meeting-actions">
          <span :class="['status-badge', `status-${m.status}`]">{{ statusLabel(m.status) }}</span>
          <Button
            icon="pi pi-trash"
            severity="danger"
            text
            size="small"
            @click.stop="onDelete(m.id)"
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
  margin-bottom: 24px;
}

.empty {
  text-align: center;
  padding: 40px;
  opacity: 0.6;
}

.meetings-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meeting-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: var(--p-content-background);
  border: 1px solid var(--p-content-border-color);
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition: background 0.15s;
}

.meeting-row:hover {
  background: var(--p-content-hover-background);
}

.meeting-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meeting-title {
  font-weight: 600;
}

.meeting-date {
  font-size: 0.85rem;
  opacity: 0.5;
}

.meeting-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-badge {
  font-size: 0.8rem;
  padding: 2px 8px;
  border-radius: 4px;
}

.status-done {
  background: var(--p-green-500);
  color: white;
}

.status-processing {
  background: var(--p-yellow-500);
  color: black;
}

.status-error {
  background: var(--p-red-500);
  color: white;
}
</style>
