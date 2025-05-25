<template>
  <h1>Welcome to <b>SupaDupaDAO</b>!</h1>
  <p>
    This is a demo DAO application built on the TON blockchain.
    You can create proposals, vote on them, and manage your DAO.
  </p>

  <p>
    To get started, choose a DAO from the list below
  </p>

  <ul>
    <li v-for="dao in daos" :key="dao.address.raw">
      <router-link :to="`/${dao.address.raw}/proposals`">
        DAO - {{ dao.address.user_friendly }}
      </router-link>
    </li>
  </ul>
</template>

<script lang="ts">
import { fetchDaoList, type DaoData } from '@/api';

export default {
  data() {
    return {
      daos: [] as DaoData[],
    }
  },
  async created() {
    const result = await fetchDaoList();
    this.daos = result.dao;
  }
}
</script>
