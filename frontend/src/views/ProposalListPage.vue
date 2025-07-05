<template>
  <div class="block" v-if="loading.length">
    <h1>Loading please vait <i class="fa-solid fa-spinner fa-spin-pulse"></i></h1>
  </div>

  <div class="block">
    <span class="dao-title">DAO Skipper</span> <span class="dao-address">{{ userFriendlyAddress }}</span>
  </div>

  <div class="block" v-if="myAddress != null && isParticipant">
    <h2>My balance</h2>
    <div class="flex">
      <div class="box flex-auto">
        <div class="text-2">Top up</div>
        <div class="flex">
          <!-- <input type="text" class="input default flex-auto" placeholder="e.g. 100500 $JETTON" disabled> -->
          <button type="button" class="button default flex" @click="lockJetton">Lock tokens</button>
        </div>
        <div class="text-3">Lock more tokens (You have {{ nanoTonToTon(Number(jettonBalance)) }} jettons, {{ nanoTonToTon(Number(lockBalance)) }} locked)</div>
      </div>
      <div class="box flex-auto">
        <div class="text-2">Faucet</div>
        <div class="flex">
          <!-- <input type="text" class="input default flex-auto" placeholder="e.g. 100500 $JETTON" disabled> -->
          <button type="button" class="button default flex" @click="jettonFaucet">Request tokens</button>
        </div>
        <div class="text-3">Get governance tokens</div>
      </div>
    </div>
  </div>
  <div class="block" v-if="myAddress != null && !isParticipant">
    <h2>Become a participant</h2>
    <div class="box flex-auto">
      <div class="text-2">Request some testnet governance tokens</div>
      <div class="flex">
        <!-- <input type="text" class="input default flex-auto" placeholder="e.g. 100500 $JETTON" disabled> -->
        <button type="button" class="button default flex" @click="jettonFaucet">Request</button>
      </div>
      <div class="text-3">After receiving reload page</div>
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
        <RouterLink to="./new_proposal">
          <button v-if="myAddress != null && isParticipant" type="button" class="button primary" >New proposal</button>
        </RouterLink>
      </div>
    </div>

    <table class="table">
      <thead>
        <tr>
          <th>#</th>
          <th>Title</th>
          <th>Status</th>
          <th>Votes (yes / no)</th>
          <th>Expires date</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="proposal in proposals" class="cursor-pointer" @click="$router.push(`./proposal/${proposal.id}`)">
          <td>{{ proposal.id }}</td>
          <td>Proposal</td>
          <td>Status</td>
          <td>{{ nanoTonToTon(proposal.votes_yes) }} / {{ nanoTonToTon(proposal.votes_no) }}</td>
          <td>{{ new Date((proposal.expires_at || 0) * 1000).toLocaleString() }} UTC</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
import { fetchDaoItem, fetchProposalsList, fetchWalletInfo, type ProposalData } from '@/api';
import { cropTonAddress, nanoTonToTon } from '@/utils';
import { Address, beginCell, Cell, toNano } from '@ton/core';
import { CHAIN } from '@tonconnect/ui';
import lockContract from "@/assets/lockContract.json";

export default {
  inject: ['wallet'],
  data() {
    return {
      loading: [] as string[],
      daoAddress: Address.parse(this.$route.params.dao as string),
      proposals: [] as ProposalData[],

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
    this.loading.push("proposalsList");
    const result = await fetchProposalsList(this.daoAddress.toString());
    this.proposals = result.proposals;
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
  computed: {
    userFriendlyAddress() {
      return cropTonAddress(this.daoAddress);
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
    nanoTonToTon,
    lockJetton() {
      const payload = beginCell()
        .storeUint(0x0f8a7ea5, 32)
        .storeUint(0, 64)
        .storeCoins(this.jettonBalance)
        .storeAddress(this.lockAddress)
        .storeAddress(this.lockAddress)
        .storeMaybeRef(null)
        .storeCoins(toNano('0.1'))
        .storeMaybeRef(null)
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
            amount: toNano('0.2').toString(),
            payload: payload.toBoc().toString('base64'),
          },
        ],
      });
    },
    jettonFaucet() {
      const payload = beginCell()
        .storeUint(0x133704, 32)
        .storeUint(0, 64)
        .storeAddress(this.myAddress)
        .storeCoins(toNano('100000'))
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
