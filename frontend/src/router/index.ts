import { createRouter, createWebHistory } from 'vue-router'
import ProposalsList from '@/views/ProposalsList.vue'
import ProposalPage from '@/views/ProposalPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'proposals_list',
      component: ProposalsList,
    },
    {
      path: '/1',
      name: 'proposal_page',
      component: ProposalPage
    },
  ],
})

export default router
