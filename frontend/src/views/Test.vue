<template>
  <div v-if="!isConnected" class="box">
    <button @click="openModal">Connect Wallet</button>
  </div>
  <div v-else class="box">
    <button @click="disconnect">Disconnect</button>
  </div>

  <div v-if="isConnected" class="box">
    <label>Your jetton lock address<input v-model="lockAddress" type="text" placeholder="EQ..."/></label>
    <hr />
    <label>Your jetton wallet address<input v-model="jettonAddress" type="text" placeholder="EQ..." /></label><br />
    <label>Tokens amount<input v-model="tokenAmount" type="number" placeholder="100500" /></label><br />
    <button @click="lockJetton">Lock tokens</button>
    <hr />
    <button @click="newProposal">New proposal</button>
  </div>

  <hr />

  <table>
    <thead>
      <tr>
        <th>№</th>
        <th>Votes</th>
        <th>Expires</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="proposal in proposals">
        <td>{{ proposal.id }}</td>
        <td>{{ proposal.votes_yes }} / {{ proposal.votes_no }}</td>
        <td>{{ proposal.expires_at }}</td>
      </tr>
    </tbody>
  </table>
</template>

<style scoped>
.box {
  border-width: 1px;
  border-style: dotted;
  padding: 10px;
  margin: 10px;
}
</style>

<script lang="ts">
import { fetchProposalsList, type ProposalData } from "@/api";
import { Address, beginCell, toNano } from "@ton/core";
import { CHAIN } from "@tonconnect/ui";

export default {
  data() {
    return {
      lockAddress: null,
      jettonAddress: null,
      tokenAmount: null,
      wallet: null,
      proposals: [] as ProposalData[],
      isConnected: false,
    }
  },
  async created() {
    const result = await fetchProposalsList(this.$route.params.dao);
    this.proposals = result.proposals;
  },
  beforeMount() {
    this.$tonConnectUI.onStatusChange((walletAndwalletInfo) => {
      this.isConnected = true;
    });
  },
  methods: {
    openModal() {
      this.$tonConnectUI.openModal();
    },
    disconnect() {
      this.$tonConnectUI.disconnect();
      this.isConnected = false;
    },
    lockJetton() {
      const payload = beginCell()
        .storeUint(0x0f8a7ea5, 32)
        .storeUint(0, 64)
        .storeCoins(this.tokenAmount || 0)
        .storeAddress(Address.parse(this.lockAddress || ""))
        .storeAddress(Address.parse(this.lockAddress || ""))
        .storeMaybeRef(null)
        .storeCoins(1)
        .endCell()

      this.$tonConnectUI.sendTransaction({
        validUntil: Math.floor(Date.now() / 1000) + 360,
        network: CHAIN.TESTNET,
        messages: [
          {
            address: this.jettonAddress || "",
            amount: toNano('0.1').toString(),
            payload: payload.toBoc().toString('base64'),
          },
        ],
      });
    },
    newProposal() {
      const payload = beginCell()
        .storeUint(0x690101, 32)
        .storeAddress(Address.parse(this.$route.params.dao))
        .storeBit(false)
        .storeRef(
          beginCell()
            .storeUint(0x690401, 32)
            .storeAddress(Address.parse("UQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJKZ"))
            .storeRef(beginCell().endCell())
            .endCell()
        )
        .endCell()

      this.$tonConnectUI.sendTransaction({
        validUntil: Math.floor(Date.now() / 1000) + 360,
        network: CHAIN.TESTNET,
        messages: [
          {
            address: this.lockAddress || "",
            amount: toNano('0.1').toString(),
            payload: payload.toBoc().toString('base64'),
          },
        ],
      });
    }
  },
}
</script>
