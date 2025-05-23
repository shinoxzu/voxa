import "./assets/main.css";
import "primeicons/primeicons.css";

import { createPinia } from "pinia";
import { createApp } from "vue";
import PrimeVue from "primevue/config";
import ToastService from "primevue/toastservice";
import Aura from "@primeuix/themes/aura";
import App from "./App.vue";

const pinia = createPinia();

const app = createApp(App);

app.use(pinia);
app.use(PrimeVue, {
  theme: {
    preset: Aura,
  },
});
app.use(ToastService);

app.mount("#app");
