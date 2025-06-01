<template>
  <div v-if="!isConnected" class="box">
    <button @click="openModal">Connect Wallet</button>
  </div>
  <div v-else class="box">
    <button @click="disconnect">Disconnect</button>
  </div>

  <div v-if="isConnected" class="box">
    <button @click="jettonFaucet">Jetton faucet</button>
    <button @click="newProposal">New proposal</button>
    <button @click="lockJetton">Lock Jetton</button>
  </div>

  <hr />

  <table>
    <thead>
      <tr>
        <th>№</th>
        <th>Votes</th>
        <th>Expires</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="proposal in proposals">
        <td>{{ proposal.id }}</td>
        <td>{{ proposal.votes_yes }} / {{ proposal.votes_no }}</td>
        <td>{{ proposal.expires_at }}</td>
        <td>
          <button @click="() => {vote(proposal.id, true)}">Vote "FOR"</button>
          <button @click="() => {vote(proposal.id, false)}">Vote "AGAINST"</button>
        </td>
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
import { fetchJettonMaster, fetchLockAddress, fetchProposalsList, fetchWalletAddress, type ProposalData } from "@/api";
import { Address, beginCell, toNano } from "@ton/core";
import { CHAIN } from "@tonconnect/ui";

export default {
  data() {
    return {
      daoAddress: Address.parse(this.$route.params.dao as string),
      lockAddress: null as Address | null,
      jettonWalletAddress: null as Address | null,
      jettonMaster: null as Address | null,
      proposals: [] as ProposalData[],
      isConnected: false,
      myAddress: null as Address | null,
    }
  },
  async created() {
    const result = await fetchProposalsList(this.daoAddress.toString());
    this.proposals = result.proposals;
  },
  beforeMount() {
    this.$tonConnectUI.onStatusChange(async (walletAndwalletInfo) => {
      this.isConnected = true;
      const myAddress = Address.parse(walletAndwalletInfo?.account.address || "");

      this.myAddress = myAddress;

      console.log("Connected to wallet", myAddress.toString());

      const jettonWalletResponse = await fetchWalletAddress(this.daoAddress.toString(), myAddress.toString());
      console.log("Jetton wallet response", jettonWalletResponse);
      this.jettonWalletAddress = Address.parse(jettonWalletResponse.address.raw);

      const lockAddressResponse = await fetchLockAddress(this.daoAddress.toString(), myAddress.toString());
      console.log("Lock address response", lockAddressResponse);
      this.lockAddress = Address.parse(lockAddressResponse.address.raw);

      const jettonMasterResponse = await fetchJettonMaster(this.daoAddress.toString());
      console.log("Lock address response", jettonMasterResponse);
      this.jettonMaster = Address.parse(jettonMasterResponse.address.raw);
    });
  },
  methods: {
    async openModal() {
      if (this.$tonConnectUI.account) {
        await this.$tonConnectUI.disconnect();
      }
      await this.$tonConnectUI.openModal();
    },
    disconnect() {
      this.$tonConnectUI.disconnect();
      this.isConnected = false;
    },
    lockJetton() {
      const payload = beginCell()
        .storeUint(0x0f8a7ea5, 32)
        .storeUint(0, 64)
        .storeCoins(1)
        .storeAddress(this.lockAddress)
        .storeAddress(this.lockAddress)
        .storeMaybeRef(null)
        .storeCoins(toNano("0.01"))
        .endCell()

      this.$tonConnectUI.sendTransaction({
        validUntil: Math.floor(Date.now() / 1000) + 360,
        network: CHAIN.TESTNET,
        messages: [
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

      this.$tonConnectUI.sendTransaction({
        validUntil: Math.floor(Date.now() / 1000) + 360,
        network: CHAIN.TESTNET,
        messages: [
          {
            address: this.lockAddress?.toString() || "",
            amount: toNano('0.1').toString(),
            payload: payload.toBoc().toString('base64'),
          },
        ],
      });
    },
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

      this.$tonConnectUI.sendTransaction({
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
    jettonFaucet() {
      const payload = beginCell()
        .storeUint(0x133704, 32)
        .storeUint(0, 64)
        .storeAddress(this.myAddress)
        .storeCoins(1)
        .endCell()

      this.$tonConnectUI.sendTransaction({
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
