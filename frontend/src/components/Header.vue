<template>
  <header class="header">
    <div class="inner">
      <div class="header-item logo">
        <a href="/"><i>SupaDupa</i><b>DAO</b></a>
      </div>

      <nav class="header-item nav-menu">
        <a href="/" class="nav-menu__item active">Home</a>
        <a href="https://docs.supadupa.space" target="_blank" class="nav-menu__item">Docs</a>
      </nav>

      <div class="header-item nav-actions">
        <a href="https://github.com/supadupadao" target="_blank"><i class="fa-brands fa-github fa-2x"></i></a>
        <div class="language-switcher">
          <i class="fa-solid fa-chevron-down"></i>
          EN
        </div>
        <div v-if="!wallet?.state.connected" @click="wallet?.openModal">
          <button type="button" class="button small orange">
            Connect wallet
          </button>
        </div>
        <div v-if="wallet?.state.connected" @click="wallet?.disconnect">{{ userFriendlyAddress }}</div>
      </div>
    </div>
  </header>
</template>

<script>
import { cropTonAddress } from '@/utils';

export default {
  inject: ['wallet'],
  computed: {
    userFriendlyAddress() {
      if (this.wallet.state.connected) {
        return cropTonAddress(this.wallet.state.address);
      } else {
        return `Wallet`
      }
    }
  }
}
</script>
