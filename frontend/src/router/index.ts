import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import ProposalListPage from '@/views/ProposalListPage.vue'
import ProposalCardPage from '@/views/ProposalCardPage.vue'
import CreateProposal from '@/views/CreateProposal.vue'

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
    {
      path: '/:dao/proposal/:proposal_id',
      name: 'proposal_card',
      component: ProposalCardPage,
    },
    {
      path: '/:dao/new_proposal/',
      name: 'new_proposal',
      component: CreateProposal,
    },
  ],
})

export default router
