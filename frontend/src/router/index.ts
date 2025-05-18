import { createRouter, createWebHistory } from 'vue-router'
import Test from '@/views/Test.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/:dao',
      name: 'proposals_list',
      component: Test,
    },
  ],
})

export default router
