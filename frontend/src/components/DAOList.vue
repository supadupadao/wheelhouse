<template>
  <ul>
    <li v-for="dao in daos" :key="dao.address.raw">
      <router-link :to="`/${dao.address.raw}/proposals`">
        <div class="border border-gray-400 rounded-md p-8">
          {{ dao.jetton_name }}
        </div>
      </router-link>
    </li>
  </ul>
</template>

<script lang="ts">
import { fetchDaoList, type DaoItem } from '@/api'

export default {
  data() {
    return {
      daos: [] as DaoItem[],
    }
  },
  async created() {
    const result = await fetchDaoList()
    this.daos = result.dao
  },
}
</script>
