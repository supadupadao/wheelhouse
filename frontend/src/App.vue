<template>
  <RouterView />
</template>

<script lang="ts">
import type { TonConnectUI } from '@tonconnect/ui';
import { RouterView } from 'vue-router'

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $tonConnectUI: TonConnectUI;
  }
}

export default {
  components: {
    RouterView
  },
};
</script>
