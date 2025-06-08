import './assets/styles/main.css'
import '@fortawesome/fontawesome-free/css/all.css';

import { createApp, reactive } from 'vue'
import App from './App.vue'
import router from './router'
import { TonConnectUI } from '@tonconnect/ui';
import { Wallet } from './wallet';

const app = createApp(App);

(async () => {
  app.use(router);

  const tonConnectUI = new TonConnectUI({
    manifestUrl: `http://dao.supadupa.space/tonconnect-manifest.json`,
  });
  const wallet = new Wallet(tonConnectUI);

  app.provide("wallet", reactive(wallet));

  app.mount('#app');
})();
