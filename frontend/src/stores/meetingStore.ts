import { ref } from "vue";
import { defineStore } from "pinia";
import { api, type Meeting, type MeetingListItem, type MeetingStatus } from "@/services/api";

export const useMeetingStore = defineStore("meeting", () => {
  const meetings = ref<MeetingListItem[]>([]);
  const currentMeeting = ref<Meeting | null>(null);
  const processingStatus = ref<MeetingStatus | null>(null);
  const isUploading = ref(false);

  let pollTimer: ReturnType<typeof setInterval> | null = null;

  async function uploadMeeting(file: Blob, title: string): Promise<string> {
    isUploading.value = true;
    try {
      const { id } = await api.createMeeting(file, title);
      startPolling(id);
      return id;
    } finally {
      isUploading.value = false;
    }
  }

  function startPolling(id: string) {
    stopPolling();
    pollTimer = setInterval(async () => {
      try {
        const status = await api.getMeetingStatus(id);
        processingStatus.value = status;
        if (status.status !== "processing") {
          stopPolling();
          await fetchMeeting(id);
        }
      } catch {
        stopPolling();
      }
    }, 2000);
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
  }

  async function fetchMeeting(id: string) {
    currentMeeting.value = await api.getMeeting(id);
  }

  async function fetchMeetings() {
    meetings.value = await api.listMeetings();
  }

  async function deleteMeeting(id: string) {
    await api.deleteMeeting(id);
    meetings.value = meetings.value.filter((m) => m.id !== id);
    if (currentMeeting.value?.id === id) {
      currentMeeting.value = null;
    }
  }

  function clearCurrent() {
    currentMeeting.value = null;
    processingStatus.value = null;
    stopPolling();
  }

  return {
    meetings,
    currentMeeting,
    processingStatus,
    isUploading,
    uploadMeeting,
    fetchMeeting,
    fetchMeetings,
    deleteMeeting,
    startPolling,
    clearCurrent,
  };
});
