// Changelog: Dec 14 22:30 added songs view to the router
// Dec 16 21:30 added result view to the router
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    {
        path: '/',
        name: 'home',
        component: () => import('../views/HomeView.vue')
    },
    {
        path: '/songs',
        name: 'songs',
        component: () => import('../views/SongsView.vue')
    },
    {
        path: '/play/:bid',
        name: 'gameplay',
        component: () => import('../views/GamePlayView.vue')
    },
    {
        path: '/result/:bid',
        name: 'result',
        component: () => import('../views/ResultView.vue')
    },
]

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes
})

export default router