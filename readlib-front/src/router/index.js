import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '@/views/HomeView.vue';
import LoginView from '@/views/auth/LoginView.vue';
import RegisterView from '@/views/auth/RegisterView.vue';
import MainPanel from '@/views/MainPanel.vue';
import DashboardView from '@/views/dashboardView.vue';
import ExamsView from '@/views/ExamsView.vue';
import LegalQueryView from '@/views/LegalQueryView.vue';
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
    {
      path: '/app',
      component: MainPanel,
      children: [
        {
          path: 'exams', 
          name: 'exams',
          component: DashboardView,
        },
        {
          path: 'exam', 
          name: 'exam',
          component: ExamsView,
        },
        {
          path: 'question', 
          name: 'question',
          component: LegalQueryView,
        },
      ],
    },
  ],
});

export default router;


