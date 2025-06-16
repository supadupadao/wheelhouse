<template>
  <div class="website">
    <Header />
    <main class="main">
      <div class="main-view">
        <RouterView />
      </div>
    </main>
    <Footer />
  </div>
</template>

<script lang="ts">
import type { TonConnectUI } from '@tonconnect/ui';
import { RouterView, type Router } from 'vue-router';
import Header from './components/Header.vue';
import Footer from './components/Footer.vue';
import type { Wallet } from './wallet';

declare module 'vue' {
  interface ComponentCustomProperties {
    wallet: Wallet;
    $router: Router;
  }
}

export default {
  components: {
    Header,
    RouterView,
    Footer,
  },
};
</script>
