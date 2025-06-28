<template>
  <div class="block" v-if="loading">
    <h1>Loading please vait <i class="fa-solid fa-spinner fa-spin-pulse"></i></h1>
  </div>

  <div class="block">
    <h1>#{{ $route.params.proposal_id }} Proposal</h1>
  </div>

  <div class="block text-center">
    <button type="button" class="button primary m-4" @click="() => {vote(Number($route.params.proposal_id as string) , true)}">Vote YES</button>
    <button type="button" class="button primary m-4" @click="() => {vote(Number($route.params.proposal_id as string) , false)}">Vote NO</button>
  </div>
</template>

<script lang="ts">
import { fetchDaoItem, fetchWalletInfo } from '@/api';
import { Address, beginCell, toNano } from '@ton/core';
import { CHAIN } from '@tonconnect/ui';

export default {
  inject: ["wallet"],
  data() {
    return {
      loading: true,
      daoAddress: Address.parse(this.$route.params.dao as string),
      myAddress: null as Address | null,
      lockAddress: null as Address | null,
      lockBalance: 0n,
      jettonWalletAddress: null as Address | null,
      jettonBalance: 0n,
      jettonMaster: null as Address | null,
    }
  },
  watch: {
    async 'wallet.state.connected'(newVal: boolean) {
      if (newVal) {
        this.loading = true;

        const myAddress = Address.parse(this.wallet?.state.address!.toString() || "");
        this.myAddress = myAddress;

        console.log("Connected to wallet", myAddress.toString());

        const [walletInfo, daoItem] = await Promise.all([
          fetchWalletInfo(this.daoAddress.toRawString(), myAddress.toRawString()),
          fetchDaoItem(this.daoAddress.toRawString()),
        ]);

        this.jettonWalletAddress = walletInfo.jetton_wallet ? Address.parse(walletInfo.jetton_wallet.address.raw) : null;
        this.lockAddress = walletInfo.lock ? Address.parse(walletInfo.lock.address.raw) : null;
        this.lockBalance = walletInfo.lock ? BigInt(walletInfo.lock.balance) : 0n;
        this.jettonMaster = Address.parse(daoItem.jetton_master.raw);
        this.jettonBalance = walletInfo.jetton_wallet ? BigInt(walletInfo.jetton_wallet.balance) : 0n;

        this.loading = false;
      }
    }
  },
  methods: {
    vote(proposalId: number, decision: boolean) {
      let startTime = Math.floor(Date.now() / 1000);

      const payload = beginCell()
        .storeUint(0x690101, 32)
        .storeAddress(Address.parse(this.$route.params.dao as string))
        .storeBit(true)
        .storeUint(startTime + 1209600, 64)
        .storeRef(
          beginCell()
            .storeUint(0x690402, 32)
            .storeUint(proposalId, 64)
            .storeBit(decision)
            .endCell()
        )
        .endCell()

      this.wallet.tonConnectUI.sendTransaction({
        validUntil: Math.floor(Date.now() / 1000) + 360,
        network: CHAIN.TESTNET,
        messages: [
          {
            address: this.lockAddress?.toString() || "",
            amount: toNano('0.2').toString(),
            payload: payload.toBoc().toString('base64'),
          },
        ],
      });
    },
  }
}
</script>
