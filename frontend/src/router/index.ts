import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import ProposalList from '@/views/ProposalList.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
    },
    {
      path: '/:dao/proposals/',
      name: 'proposals_list',
      component: ProposalList,
    },
  ],
})

export default router
