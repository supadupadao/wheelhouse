<template>
  <div class="block" v-if="loading">
    <h1>Loading please vait <i class="fa-solid fa-spinner fa-spin-pulse"></i></h1>
  </div>

  <div class="block">
    <span class="dao-title">DAO Skipper</span> <span class="dao-address">{{ userFriendlyAddress }}</span>
  </div>

  <div class="block" v-if="wallet?.state.connected">
    <h2>My balance</h2>
    <div class="flex">
      <div class="box flex-auto">
        <div class="text-2">Top up</div>
        <div class="flex">
          <input type="text" class="input default flex-auto" placeholder="e.g. 100500 $JETTON" disabled>
          <button type="button" class="button default flex" @click="lockJetton">Submit</button>
        </div>
        <div class="text-3">Lock more tokens</div>
      </div>
      <div class="box flex-auto">
        <div class="text-2">Faucet</div>
        <div class="flex">
          <input type="text" class="input default flex-auto" placeholder="e.g. 100500 $JETTON" disabled>
          <button type="button" class="button default flex" @click="jettonFaucet">Submit</button>
        </div>
        <div class="text-3">Get governance tokens</div>
      </div>
    </div>
  </div>

  <div class="block">
    <h2>Proposals</h2>

    <div class="proposals-actions">
      <div>
        <button type="button" class="button max">Active</button>
        <button type="button" class="button max disabled">Closed</button>
      </div>
      <div>
        <button type="button" class="button primary" @click="newProposal">New proposal</button>
      </div>
    </div>

    <table class="table">
      <thead>
        <tr>
          <th>#</th>
          <th>Title</th>
          <th>Status</th>
          <th>Votes</th>
          <th>Date</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="proposal in proposals" class="cursor-pointer" @click="$router.push(`./proposal/${proposal.id}`)">
          <td>{{ proposal.id }}</td>
          <td>Proposal</td>
          <td>Status</td>
          <td>{{ proposal.votes_yes }} - {{ proposal.votes_no }}</td>
          <td>{{ proposal.expires_at }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
import { fetchDaoItem, fetchProposalsList, fetchWalletInfo, type ProposalData } from '@/api';
import { cropTonAddress } from '@/utils';
import { Address, beginCell, Cell, toNano } from '@ton/core';
import { CHAIN } from '@tonconnect/ui';
import lockContract from "@/assets/lockContract.json";

export default {
  inject: ['wallet'],
  data() {
    return {
      loading: true,
      daoAddress: Address.parse(this.$route.params.dao as string),
      proposals: [] as ProposalData[],

      myAddress: null as Address | null,
      lockAddress: null as Address | null,
      lockBalance: 0n,
      jettonWalletAddress: null as Address | null,
      jettonBalance: 0n,
      jettonMaster: null as Address | null,
    }
  },
  async created() {
    const result = await fetchProposalsList(this.daoAddress.toString());
    this.proposals = result.proposals;
    this.loading = false;
  },
  computed: {
    userFriendlyAddress() {
      return cropTonAddress(this.daoAddress);
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
    lockJetton() {
      const payload = beginCell()
        .storeUint(0x0f8a7ea5, 32)
        .storeUint(0, 64)
        .storeCoins(1)
        .storeAddress(this.lockAddress)
        .storeAddress(this.lockAddress)
        .storeMaybeRef(null)
        .storeCoins(1)
        .endCell();

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
            amount: toNano('0.1').toString(),
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
          {
            address: this.jettonWalletAddress?.toString() || "",
            amount: toNano('0.1').toString(),
            payload: payload.toBoc().toString('base64'),
          },
        ],
      });
    },
    newProposal() {
      const payload = beginCell()
        .storeUint(0x690101, 32)
        .storeAddress(Address.parse(this.$route.params.dao as string))
        .storeBit(false)
        .storeRef(
          beginCell()
            .storeUint(0x690401, 32)
            .storeAddress(Address.parse("UQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJKZ"))
            .storeRef(beginCell().endCell())
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
            amount: toNano('0.1').toString(),
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
    jettonFaucet() {
      const payload = beginCell()
        .storeUint(0x133704, 32)
        .storeUint(0, 64)
        .storeAddress(this.myAddress)
        .storeCoins(1)
        .endCell()

      this.wallet?.tonConnectUI.sendTransaction({
        validUntil: Math.floor(Date.now() / 1000) + 360,
        network: CHAIN.TESTNET,
        messages: [
          {
            address: this.jettonMaster?.toString() || "",
            amount: toNano('0.2').toString(),
            payload: payload.toBoc().toString('base64'),
          },
        ],
      });
    }
  },
}
</script>
