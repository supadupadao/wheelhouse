<template>
  <h1>Welcome to <b>SupaDupaDAO</b>!</h1>
  <p>
    This is a demo DAO application built on the TON blockchain.
    You can create proposals, vote on them, and manage your DAO.
  </p>

  <p>
    To get started, choose a DAO from the list below
  </p>

  <DAOList />
</template>

<script lang="ts">
import DAOList from '@/components/DAOList.vue';

export default {
  components: {
    DAOList,
  },
}
</script>
