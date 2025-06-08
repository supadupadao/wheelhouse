<template>
  <div class="block">
    <span class="dao-title">DAO Skipper</span> <span class="dao-address">{{ daoAddress }}</span>
  </div>

  <div class="block">
    <h1>Proposals</h1>

    <div class="proposals-actions">
      <div>
        <button type="button" class="button">All proposals</button>
        <button type="button" class="button outline">Open</button>
        <button type="button" class="button outline">Closed</button>
      </div>
      <div>
        <button type="button" class="button gradient">New proposal</button>
      </div>
    </div>

    <table class="table">
      <thead>
        <tr>
          <th>№</th>
          <th>Title</th>
          <th>Status</th>
          <th>Votes</th>
          <th>Date</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="proposal in proposals">
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
import { fetchProposalsList, type ProposalData } from '@/api';
import { Address } from '@ton/core';

export default {
  data() {
    return {
      daoAddress: Address.parse(this.$route.params.dao as string),
      proposals: [] as ProposalData[],
    }
  },
  async created() {
    const result = await fetchProposalsList(this.daoAddress.toString());
    this.proposals = result.proposals;
  },
}

// import { fetchJettonMaster, fetchLockAddress, fetchProposalsList, fetchWalletAddress, type ProposalData } from "@/api";
// import { Address, beginCell, Cell, toNano } from "@ton/core";
// import { CHAIN } from "@tonconnect/ui";
// import lockContract from "@/assets/lockContract.json";

// export default {
//   data() {
//     return {
//       loading: true,
//       daoAddress: Address.parse(this.$route.params.dao as string),
//       lockAddress: null as Address | null,
//       jettonWalletAddress: null as Address | null,
//       jettonMaster: null as Address | null,
//       proposals: [] as ProposalData[],
//       isConnected: false,
//       myAddress: null as Address | null,
//     }
//   },
//   async created() {
//     const result = await fetchProposalsList(this.daoAddress.toString());
//     this.proposals = result.proposals;
//     this.loading = false;
//   },
//   beforeMount() {
//     this.$tonConnectUI.onStatusChange(async (walletAndwalletInfo) => {
//       this.loading = true;

//       this.isConnected = true;
//       const myAddress = Address.parse(walletAndwalletInfo?.account.address || "");

//       this.myAddress = myAddress;

//       console.log("Connected to wallet", myAddress.toString());

//       const jettonWalletResponse = await fetchWalletAddress(this.daoAddress.toString(), myAddress.toString());
//       console.log("Jetton wallet response", jettonWalletResponse);
//       this.jettonWalletAddress = Address.parse(jettonWalletResponse.address.raw);

//       const lockAddressResponse = await fetchLockAddress(this.daoAddress.toString(), myAddress.toString());
//       console.log("Lock address response", lockAddressResponse);
//       this.lockAddress = Address.parse(lockAddressResponse.address.raw);

//       const jettonMasterResponse = await fetchJettonMaster(this.daoAddress.toString());
//       console.log("Jetton master response", jettonMasterResponse);
//       this.jettonMaster = Address.parse(jettonMasterResponse.address.raw);

//       this.loading = false;
//     });
//   },
//   methods: {
//     async openModal() {
//       if (this.$tonConnectUI.account) {
//         await this.$tonConnectUI.disconnect();
//       }
//       await this.$tonConnectUI.openModal();
//     },
//     disconnect() {
//       this.$tonConnectUI.disconnect();
//       this.isConnected = false;
//     },
//     lockJetton() {
//       const payload = beginCell()
//         .storeUint(0x0f8a7ea5, 32)
//         .storeUint(0, 64)
//         .storeCoins(1)
//         .storeAddress(this.lockAddress)
//         .storeAddress(this.lockAddress)
//         .storeMaybeRef(null)
//         .storeCoins(toNano("0.01"))
//         .endCell();

//       const codeCell = Cell.fromBase64(lockContract.code);
//       const systemCell = Cell.fromBase64(lockContract.system);
//       const initData = beginCell()
//         .storeRef(systemCell)
//         .storeUint(0, 1)
//         .storeAddress(this.myAddress)
//         .storeAddress(this.jettonMaster!)
//         .endCell();

//       this.$tonConnectUI.sendTransaction({
//         validUntil: Math.floor(Date.now() / 1000) + 360,
//         network: CHAIN.TESTNET,
//         messages: [
//           {
//             address: this.lockAddress?.toString() || "",
//             amount: toNano('0.1').toString(),
//             stateInit: beginCell()
//               .storeBit(false)
//               .storeBit(false)
//               .storeMaybeRef(codeCell)
//               .storeMaybeRef(initData)
//               .storeUint(0, 1)
//               .endCell()
//               .toBoc()
//               .toString('base64'),
//           },
//           {
//             address: this.jettonWalletAddress?.toString() || "",
//             amount: toNano('0.1').toString(),
//             payload: payload.toBoc().toString('base64'),
//           },
//         ],
//       });
//     },
//     newProposal() {
//       const payload = beginCell()
//         .storeUint(0x690101, 32)
//         .storeAddress(Address.parse(this.$route.params.dao as string))
//         .storeBit(false)
//         .storeRef(
//           beginCell()
//             .storeUint(0x690401, 32)
//             .storeAddress(Address.parse("UQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJKZ"))
//             .storeRef(beginCell().endCell())
//             .endCell()
//         )
//         .endCell()

//       const codeCell = Cell.fromBase64(lockContract.code);
//       const systemCell = Cell.fromBase64(lockContract.system);
//       const initData = beginCell()
//         .storeRef(systemCell)
//         .storeUint(0, 1)
//         .storeAddress(this.myAddress)
//         .storeAddress(this.jettonMaster!)
//         .endCell();

//       this.$tonConnectUI.sendTransaction({
//         validUntil: Math.floor(Date.now() / 1000) + 360,
//         network: CHAIN.TESTNET,
//         messages: [
//           {
//             address: this.lockAddress?.toString() || "",
//             amount: toNano('0.1').toString(),
//             payload: payload.toBoc().toString('base64'),
//             stateInit: beginCell()
//               .storeBit(false)
//               .storeBit(false)
//               .storeMaybeRef(codeCell)
//               .storeMaybeRef(initData)
//               .storeUint(0, 1)
//               .endCell()
//               .toBoc()
//               .toString('base64'),
//           },
//         ],
//       });
//     },
//     vote(proposalId: number, decision: boolean) {
//       let startTime = Math.floor(Date.now() / 1000);

//       const payload = beginCell()
//         .storeUint(0x690101, 32)
//         .storeAddress(Address.parse(this.$route.params.dao as string))
//         .storeBit(true)
//         .storeUint(startTime + 1209600, 64)
//         .storeRef(
//           beginCell()
//             .storeUint(0x690402, 32)
//             .storeUint(proposalId, 64)
//             .storeBit(decision)
//             .endCell()
//         )
//         .endCell()

//       this.$tonConnectUI.sendTransaction({
//         validUntil: Math.floor(Date.now() / 1000) + 360,
//         network: CHAIN.TESTNET,
//         messages: [
//           {
//             address: this.lockAddress?.toString() || "",
//             amount: toNano('0.6').toString(),
//             payload: payload.toBoc().toString('base64'),
//           },
//         ],
//       });
//     },
//     jettonFaucet() {
//       const payload = beginCell()
//         .storeUint(0x133704, 32)
//         .storeUint(0, 64)
//         .storeAddress(this.myAddress)
//         .storeCoins(1)
//         .endCell()

//       this.$tonConnectUI.sendTransaction({
//         validUntil: Math.floor(Date.now() / 1000) + 360,
//         network: CHAIN.TESTNET,
//         messages: [
//           {
//             address: this.jettonMaster?.toString() || "",
//             amount: toNano('0.2').toString(),
//             payload: payload.toBoc().toString('base64'),
//           },
//         ],
//       });
//     }
//   },
// }
</script>
