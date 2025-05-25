<template>
  <RouterView />
</template>

<script lang="ts">
import type { TonConnectUI } from '@tonconnect/ui';
import { RouterView, type Router } from 'vue-router';

declare module 'vue' {
  interface ComponentCustomProperties {
    $tonConnectUI: TonConnectUI;
    $router: Router;
  }
}

export default {
  components: {
    RouterView
  },
};
</script>
