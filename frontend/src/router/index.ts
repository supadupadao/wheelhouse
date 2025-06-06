import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import ProposalListPage from '@/views/ProposalListPage.vue'

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
      component: ProposalListPage,
    },
  ],
})

export default router
