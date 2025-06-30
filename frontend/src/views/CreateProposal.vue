<template>
  <div class="block" v-if="loading.length">
    <h1>Loading please vait <i class="fa-solid fa-spinner fa-spin-pulse"></i></h1>
  </div>

  <div class="block">
    <h1>Creating new proposal</h1>
  </div>

  <div class="block max-w-md">
    <input type="text" class="input default w-full max-w-md" placeholder="Proposal receiver address" v-model="proposalReceiver">
    <input type="text" class="input default w-full max-w-md" placeholder="Proposal payload in base64" v-model="proposalPayload">
    <input type="number" class="input default w-full max-w-md" placeholder="Proposal amount in nanoTONs" v-model.number="proposalAmount">
  </div>

  <div class="block">
    <button type="button" class="button primary" @click="newProposal">Create proposal</button>
  </div>
</template>

<script lang="ts">
import { fetchDaoItem, fetchProposalItem, fetchWalletInfo, type ProposalData } from '@/api';
import { Address, beginCell, Cell, toNano } from '@ton/core';
import { CHAIN } from '@tonconnect/ui';
import lockContract from "@/assets/lockContract.json";

export default {
  inject: ["wallet"],
  data() {
    return {
      loading: [] as string[],
      daoAddress: Address.parse(this.$route.params.dao as string),

      proposalReceiver: "",
      proposalPayload: beginCell().endCell().toBoc().toString('base64'),
      proposalAmount: toNano('0.1'),

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

        this.myAddress = Address.parse(this.wallet?.state.address!.toString() || "");

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
    }
  },
  methods: {
    newProposal() {
      const payload = beginCell()
        .storeUint(0x690101, 32)
        .storeAddress(Address.parse(this.$route.params.dao as string))
        .storeBit(false)
        .storeRef(
          beginCell()
            .storeUint(0x690401, 32)
            .storeAddress(Address.parse(this.proposalReceiver))
            .storeRef(Cell.fromBase64(this.proposalPayload))
            .endCell()
        )
        .endCell()

      const codeCell = Cell.fromBase64(lockContract.code);
      const systemCell = Cell.fromBase64(lockContract.system);
      const initData = beginCell()
        .storeRef(systemCell)
        .storeUint(0, 1)
        .storeAddress(this.myAddress)
        .storeAddress(this.jettonMaster!)
        .endCell();

      this.wallet?.tonConnectUI.sendTransaction({
        validUntil: Math.floor(Date.now() / 1000) + 360,
        network: CHAIN.TESTNET,
        messages: [
          {
            address: this.lockAddress?.toString() || "",
            amount: this.proposalAmount.toString(),
            payload: payload.toBoc().toString('base64'),
            stateInit: beginCell()
              .storeBit(false)
              .storeBit(false)
              .storeMaybeRef(codeCell)
              .storeMaybeRef(initData)
              .storeUint(0, 1)
              .endCell()
              .toBoc()
              .toString('base64'),
          },
        ],
      });
    },
  }
}
</script>
