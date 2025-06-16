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
import { fetchJettonMaster, fetchLockAddress, fetchWalletAddress } from '@/api';
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
      jettonWalletAddress: null as Address | null,
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

        const [jettonWalletResponse, lockAddressResponse, jettonMasterResponse] = await Promise.all([
          fetchWalletAddress(this.daoAddress.toString(), myAddress.toString()),
          fetchLockAddress(this.daoAddress.toString(), myAddress.toString()),
          fetchJettonMaster(this.daoAddress.toString())
        ]);

        console.log("Jetton wallet response", jettonWalletResponse);
        this.jettonWalletAddress = Address.parse(jettonWalletResponse.address.raw);

        console.log("Lock address response", lockAddressResponse);
        this.lockAddress = Address.parse(lockAddressResponse.address.raw);

        console.log("Jetton master response", jettonMasterResponse);
        this.jettonMaster = Address.parse(jettonMasterResponse.address.raw);

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
