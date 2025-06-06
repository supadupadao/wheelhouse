import './assets/main.css'
import '@fortawesome/fontawesome-free/css/all.css';

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { TonConnectUI } from '@tonconnect/ui';

const app = createApp(App);

(async () => {
  app.use(router);

  const tonConnectUI = new TonConnectUI({
    manifestUrl: `http://dao.supadupa.space/tonconnect-manifest.json`,
  });

  app.config.globalProperties.$tonConnectUI = tonConnectUI;

  app.mount('#app');
})();
