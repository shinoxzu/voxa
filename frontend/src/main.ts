import "./assets/main.css";
import "primeicons/primeicons.css";

import { createPinia } from "pinia";
import { createApp } from "vue";
import PrimeVue from "primevue/config";
import ConfirmationService from "primevue/confirmationservice";
import ToastService from "primevue/toastservice";
import Aura from "@primeuix/themes/aura";
import App from "./App.vue";
import router from "./router";

const pinia = createPinia();

const app = createApp(App);

app.use(pinia);
app.use(router);
app.use(PrimeVue, {
  theme: {
    preset: Aura,
  },
});
app.use(ToastService);
app.use(ConfirmationService);

app.mount("#app");
