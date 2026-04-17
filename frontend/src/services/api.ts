const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export interface TranscriptSegment {
  start: number;
  end: number;
  speaker: string;
  text: string;
}

export interface TrackerIssue {
  key: string;
  url: string;
}

export interface ActionItem {
  id: number;
  assignee: string;
  task: string;
  deadline: string | null;
  tracker_issue: TrackerIssue | null;
}

export interface ProcessingSteps {
  transcription: string;
  diarization: string;
  analysis: string;
}

export interface MeetingStatus {
  status: "processing" | "done" | "error";
  step: string | null;
  steps: ProcessingSteps;
}

export interface Meeting {
  id: string;
  title: string;
  created_at: string;
  status: "processing" | "done" | "error";
  duration_sec: number | null;
  transcript: TranscriptSegment[] | null;
  summary: string | null;
  action_items: ActionItem[] | null;
}

export interface MeetingListItem {
  id: string;
  title: string;
  created_at: string;
  status: "processing" | "done" | "error";
  duration_sec: number | null;
}

export const api = {
  async createMeeting(file: Blob, title: string): Promise<{ id: string }> {
    const form = new FormData();
    form.append("file", file, "audio.wav");
    const resp = await fetch(`${API_BASE}/meetings?title=${encodeURIComponent(title)}`, {
      method: "POST",
      body: form,
    });
    if (!resp.ok) throw new Error("Failed to create meeting");
    return resp.json();
  },

  async getMeeting(id: string): Promise<Meeting> {
    const resp = await fetch(`${API_BASE}/meetings/${id}`);
    if (!resp.ok) throw new Error("Meeting not found");
    return resp.json();
  },

  async getMeetingStatus(id: string): Promise<MeetingStatus> {
    const resp = await fetch(`${API_BASE}/meetings/${id}/status`);
    if (!resp.ok) throw new Error("Failed to get status");
    return resp.json();
  },

  async listMeetings(): Promise<MeetingListItem[]> {
    const resp = await fetch(`${API_BASE}/meetings`);
    if (!resp.ok) throw new Error("Failed to list meetings");
    return resp.json();
  },

  async deleteMeeting(id: string): Promise<void> {
    const resp = await fetch(`${API_BASE}/meetings/${id}`, { method: "DELETE" });
    if (!resp.ok) throw new Error("Failed to delete meeting");
  },

  async createIssue(
    meetingId: string,
    itemId: number,
    data: { summary: string; assignee?: string; deadline?: string; queue: string },
  ): Promise<TrackerIssue> {
    const resp = await fetch(
      `${API_BASE}/meetings/${meetingId}/action-items/${itemId}/create-issue`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      },
    );
    if (!resp.ok) throw new Error("Failed to create issue");
    return resp.json();
  },
};
