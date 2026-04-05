import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const HomeView = () => import('../views/HomeView.vue')
const LoginView = () => import('../views/LoginView.vue')
const RegisterView = () => import('../views/RegisterView.vue')
const ProfileView = () => import('../views/ProfileView.vue')
const DashboardView = () => import('../views/DashboardView.vue')
const SearchView = () => import('../views/SearchView.vue')
const CartView = () => import('../views/CartView.vue')
const CheckoutView = () => import('../views/CheckoutView.vue')
const AdminDashboard = () => import('../views/AdminDashboard.vue')
const AdminStats = () => import('../views/AdminStats.vue')
const AdminUsers = () => import('../views/AdminUsers.vue')
const AdminProducts = () => import('../views/AdminProducts.vue')
const AdminCategories = () => import('../views/AdminCategories.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/login', name: 'login', component: LoginView, meta: { guest: true } },
    { path: '/register', name: 'register', component: RegisterView, meta: { guest: true } },
    { path: '/profile', name: 'profile', component: ProfileView, meta: { auth: true } },
    { path: '/dashboard', name: 'dashboard', component: DashboardView, meta: { auth: true, developer: true } },
    { path: '/search', name: 'search', component: SearchView },
    { path: '/cart', name: 'cart', component: CartView },
    { path: '/checkout', name: 'checkout', component: CheckoutView, meta: { auth: true } },
    {
      path: '/admin',
      component: AdminDashboard,
      meta: { auth: true, admin: true },
      children: [
        { path: '', name: 'admin', component: AdminStats },
        { path: 'users', name: 'admin-users', component: AdminUsers },
        { path: 'products', name: 'admin-products', component: AdminProducts },
        { path: 'categories', name: 'admin-categories', component: AdminCategories }
      ]
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()
  
  if (to.meta.auth && !auth.isAuthenticated) {
    next('/login')
  } else if (to.meta.guest && auth.isAuthenticated) {
    next('/')
  } else if (to.meta.developer && !auth.isDeveloper && !auth.isSuperuser) {
    next('/')
  } else if (to.meta.admin && !['admin', 'superuser'].includes(auth.user?.role)) {
    next('/')
  } else {
    next()
  }
})

export default router