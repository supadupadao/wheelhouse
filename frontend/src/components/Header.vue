<template>
  <header class="header">
    <div class="inner">
      <div class="header-item logo">
        <a href="/"><i>SupaDupa</i><b>DAO</b></a>
      </div>

      <nav class="header-item nav-menu">
        <a href="/" class="nav-menu__item button link">Home</a>
        <a href="https://docs.supadupa.space" target="_blank" class="nav-menu__item button link disabled">Docs</a>
      </nav>

      <div class="header-item nav-actions">
        <a href="https://github.com/supadupadao" target="_blank"><i class="fa-brands fa-github fa-2x"></i></a>
        <div class="button language">
          <i class="fa-solid fa-chevron-down"></i>
          Language
        </div>
        <div v-if="!wallet?.state.connected" @click="wallet?.openModal" class="button max">Connect</div>
        <div v-if="wallet?.state.connected" @click="wallet?.disconnect">{{ userFriendlyAddress }}</div>
      </div>
    </div>
  </header>
</template>

<script lang="ts">
import { cropTonAddress } from '@/utils';

export default {
  inject: ['wallet'],
  computed: {
    userFriendlyAddress() {
      if (this.wallet.state.connected) {
        return cropTonAddress(this.wallet.state.address!);
      } else {
        return `Wallet`
      }
    }
  }
}
</script>
