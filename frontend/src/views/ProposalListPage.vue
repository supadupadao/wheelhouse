<template>
  <div class="block">
    <span class="dao-title">DAO Skipper</span> <span class="dao-address">{{ daoAddress }}</span><i v-if="loading" class="fa-solid fa-spinner fa-spin-pulse"></i>
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
      loading: true,
      daoAddress: Address.parse(this.$route.params.dao as string),
      proposals: [] as ProposalData[],
    }
  },
  async created() {
    const result = await fetchProposalsList(this.daoAddress.toString());
    this.proposals = result.proposals;
    this.loading = false;
  },
}
</script>
