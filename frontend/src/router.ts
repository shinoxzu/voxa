import { createRouter, createWebHistory } from "vue-router";
import HomePage from "@/pages/HomePage.vue";
import MeetingPage from "@/pages/MeetingPage.vue";
import HistoryPage from "@/pages/HistoryPage.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: HomePage },
    { path: "/meetings", component: HistoryPage },
    { path: "/meetings/:id", component: MeetingPage, props: true },
  ],
});

export default router;
