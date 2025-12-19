// Changelog: Dec 14 22:30 added songs view to the router
// Dec 16 21:30 added result view to the router
// Dec 18 21:00 added beatmapset detail, leaderboard, personal view of the project
// Dec 19 22:00 added forum view
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    {
        // Zheng Wu: change the default page to the forum view
        path: '/',
        name: 'home',
        component: () => import('../views/ForumView.vue')
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
    {
        path: '/me',
        name: 'me',
        component: () => import('../views/ProfileView.vue')
    },
    {
        path: '/rankings',
        name: 'rankings',
        component: () => import('../views/RankingsView.vue')
    },
    {
        path: '/profile/:uid?',
        name: 'profile',
        component: () => import('../views/ProfileView.vue')
    },
    {
        path: '/beatmap/:sid',
        name: 'beatmap-detail',
        component: () => import('../views/BeatmapDetailView.vue')
    },
    {
        path: '/forum',
        name: 'forum',
        component: () => import('../views/ForumView.vue')
    },
    {
        path: '/forum/subforum/:id',
        name: 'subforum',
        component: () => import('../views/SubforumView.vue')
    },
    {
        path: '/forum/thread/:id',
        name: 'thread',
        component: () => import('../views/ThreadView.vue')
    },
]

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes
})

export default router