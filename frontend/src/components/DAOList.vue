<template>
  <ul>
    <li v-for="dao in daos" :key="dao.address.raw">
      <router-link :to="`/${dao.address.raw}/proposals`">
        <div class="border border-gray-400 rounded-md p-8">
          DAO - {{ dao.address.user_friendly }}
        </div>
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
