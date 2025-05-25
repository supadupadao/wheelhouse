import { createRouter, createWebHistory } from 'vue-router'
import Proposals from '@/views/Proposals.vue'
import Home from '@/views/Home.vue'

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
      component: Proposals,
    },
  ],
})

export default router
