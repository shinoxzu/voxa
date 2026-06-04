<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
  <main class="app-container">
    <nav class="app-nav">
      <RouterLink to="/" class="nav-brand">Voxa</RouterLink>
      <div class="nav-links">
        <RouterLink to="/">Новая встреча</RouterLink>
        <RouterLink to="/meetings">История</RouterLink>
      </div>
    </nav>
    <div class="content-wrapper">
      <RouterView />
    </div>
  </main>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--p-content-background);
}

.app-nav {
  display: flex;
  align-items: center;
  padding: 12px 24px;
  background-color: var(--p-content-background);
  border-bottom: 1px solid var(--p-content-border-color);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  gap: 24px;
}

.nav-brand {
  font-size: 1.4rem;
  font-weight: 700;
  text-decoration: none;
  color: var(--p-primary-color);
}

.nav-links {
  display: flex;
  gap: 16px;
}

.nav-links a {
  text-decoration: none;
  color: var(--p-text-color);
  opacity: 0.7;
  transition: opacity 0.2s;
}

.nav-links a:hover,
.nav-links a.router-link-exact-active {
  opacity: 1;
}

.content-wrapper {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 20px;
}
</style>
