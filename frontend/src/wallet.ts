import { Address } from "@ton/core";
import type { TonConnectUI } from "@tonconnect/ui";
import { reactive } from "vue";

export interface State {
  connected: boolean;
  address?: Address;
};

export class Wallet {
  public tonConnectUI: TonConnectUI;
  public state: State;

  constructor(tonConnectUI: TonConnectUI) {
    this.tonConnectUI = tonConnectUI;
    this.state = reactive({
      connected: false
    });

    this.tonConnectUI.onStatusChange(async (walletAndwalletInfo) => {
      this.state.connected = true;
      this.state.address = Address.parse(walletAndwalletInfo?.account.address || "");
    });
  }

  public async openModal() {
    await this.tonConnectUI.openModal();
  }

  public async disconnect() {
    await this.tonConnectUI.disconnect();
  }
}
