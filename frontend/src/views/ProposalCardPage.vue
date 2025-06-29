<template>
  <div class="block" v-if="loading.length">
    <h1>Loading please vait <i class="fa-solid fa-spinner fa-spin-pulse"></i></h1>
  </div>

  <div class="block">
    <h1>Proposal # {{ proposal?.id }}</h1>
    <h2>{{ proposal?.address.user_friendly }}</h2>
  </div>

  <div class="block">
    <h2>My balance</h2>
    <div class="flex">
      <div class="box flex-auto">
        <div class="text-2">{{ proposal?.votes_yes }} Votes YES</div>
        <div class="flex">
          <button v-if="wallet?.state.connected && isParticipant" type="button" class="button primary m-4" @click="() => {vote(Number($route.params.proposal_id as string) , true)}">Vote YES</button>
        </div>
        <div class="text-3">{{ proposal?.votes_yes }} supported this proposal</div>
      </div>
      <div class="box flex-auto">
        <div class="text-2">{{ proposal?.votes_no }} Votes NO</div>
        <div class="flex">
          <button v-if="wallet?.state.connected && isParticipant" type="button" class="button primary m-4" @click="() => {vote(Number($route.params.proposal_id as string) , false)}">Vote NO</button>
        </div>
        <div class="text-3">{{ proposal?.votes_no }} did not support this proposal</div>
      </div>
    </div>
  </div>

  <div class="block">
    <h2>Proposal expires at</h2>
    <div class="text-2">{{ new Date((proposal?.expires_at || 0) * 1000).toLocaleString() }} UTC</div>
  </div>
</template>

<script lang="ts">
import { fetchDaoItem, fetchProposalItem, fetchWalletInfo, type ProposalData } from '@/api';
import { Address, beginCell, toNano } from '@ton/core';
import { CHAIN } from '@tonconnect/ui';

export default {
  inject: ["wallet"],
  data() {
    return {
      loading: [] as string[],
      daoAddress: Address.parse(this.$route.params.dao as string),
      proposal: null as ProposalData | null,
      myAddress: null as Address | null,
      isParticipant: false,
      lockAddress: null as Address | null,
      lockBalance: 0n,
      jettonWalletAddress: null as Address | null,
      jettonBalance: 0n,
      jettonMaster: null as Address | null,
    }
  },
  async created() {
    this.loading.push("proposalData");
    const result = await fetchProposalItem(this.daoAddress.toRawString(), Number(this.$route.params.proposal_id));
    this.proposal = result;
    this.loading.pop();

    if (this.wallet?.state.address) {
      this.loading.push("wallet");

      this.myAddress = Address.parse(this.wallet.state.address.toString());

      const [walletInfo, daoItem] = await Promise.all([
        fetchWalletInfo(this.daoAddress.toRawString(), this.myAddress.toRawString()),
        fetchDaoItem(this.daoAddress.toRawString()),
      ]);

      this.isParticipant = walletInfo.is_participant;
      this.jettonWalletAddress = walletInfo.jetton_wallet ? Address.parse(walletInfo.jetton_wallet.address.raw) : null;
      this.lockAddress = walletInfo.lock ? Address.parse(walletInfo.lock.address.raw) : null;
      this.lockBalance = walletInfo.lock ? BigInt(walletInfo.lock.balance) : 0n;
      this.jettonMaster = Address.parse(daoItem.jetton_master.raw);
      this.jettonBalance = walletInfo.jetton_wallet ? BigInt(walletInfo.jetton_wallet.balance) : 0n;

      this.loading.pop();
    }
  },
  watch: {
    async 'wallet.state.connected'(newVal: boolean) {
      if (newVal) {
        this.loading.push("wallet");

        const myAddress = Address.parse(this.wallet?.state.address!.toString() || "");
        this.myAddress = myAddress;

        console.log("Connected to wallet", myAddress.toString());

        const [walletInfo, daoItem] = await Promise.all([
          fetchWalletInfo(this.daoAddress.toRawString(), myAddress.toRawString()),
          fetchDaoItem(this.daoAddress.toRawString()),
        ]);

        this.isParticipant = walletInfo.is_participant;
        this.jettonWalletAddress = walletInfo.jetton_wallet ? Address.parse(walletInfo.jetton_wallet.address.raw) : null;
        this.lockAddress = walletInfo.lock ? Address.parse(walletInfo.lock.address.raw) : null;
        this.lockBalance = walletInfo.lock ? BigInt(walletInfo.lock.balance) : 0n;
        this.jettonMaster = Address.parse(daoItem.jetton_master.raw);
        this.jettonBalance = walletInfo.jetton_wallet ? BigInt(walletInfo.jetton_wallet.balance) : 0n;

        this.loading.pop();
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
