<script setup lang="ts">
import MainPage from "./components/MainPage.vue";
</script>

<template>
  <main class="app-container">
    <div class="content-wrapper">
      <MainPage />
    </div>
  </main>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--surface-b);
}

.content-wrapper {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 20px;
}
</style>
