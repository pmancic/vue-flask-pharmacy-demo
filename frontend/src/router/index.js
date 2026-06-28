import { createRouter, createWebHistory } from 'vue-router'
import ProductsView from "@/views/ProductsView.vue";
import RegisterView from "@/views/RegisterView.vue";
import LoginView from "@/views/LoginView.vue";
import profileView from "@/views/ProfileView.vue";
import CartView from "@/views/CartView.vue";
import AddProductView from "@/views/AddProductView.vue";
import EditProductView from "@/views/EditProductView.vue";
import AdminUsersView from "@/views/AdminUsersView.vue";
import AdminProductsView from "@/views/AdminProductsView.vue";
import AdminCommentsView from "@/views/AdminCommentsView.vue";
import ProductDetailsView from "@/views/ProductDetailsView.vue";
import AdminAddUserView from "@/views/AdminAddUserView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      redirect: '/products'
    },
    {
      path: '/products',
      name: 'svi_proizvodi',
      component: ProductsView,
      meta: {requiresAuth: true}
    },
    {
      path: "/products/:id",
      component: ProductDetailsView,
      name: 'detaljno_proizvod',
      meta: { requiresAuth: true }
    },
    {
      path: '/products/add',
      component: AddProductView,
      name: 'dodaj_proizvod',
      meta: { requiresAuth: true, requiresSeller: true }
    },
    {
      path: '/products/edit/:id',
      component: EditProductView,
      name: 'izmeni_prizovd',
      meta: { requiresAuth: true, requiresSeller: true }
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/profile/:username',
      component: profileView,
      name: 'profil',
      meta: { requiresAuth: true }
    },
    {
      path: '/cart',
      name: 'cart',
      component: CartView,
      meta: {requiresAuth: true}
    },
    {
      path: "/admin/users",
      component: AdminUsersView,
      name: 'admin_korisnici',
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: "/admin/users/add",
      name: "admin_dodaj_korisnika",
      component: AdminAddUserView,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: "/admin/products",
      name: 'admin_proizvodi',
      component: AdminProductsView,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: "/admin/comments",
      name: 'admin_komentari',
      component: AdminCommentsView,
      meta: { requiresAuth: true, requiresAdmin: true }
    }
  ],
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role");

  if (to.meta?.requiresAuth && !token)
    return next("/login");
  if (to.meta?.requiresAdmin && role !== "administrator")
    return next("/products");
  if (to.meta?.requiresSeller && !(role === "prodavac" || role === "administrator"))
    return next("/products");
  if (to.path === '/products' && role === 'administrator') {
    next('/admin/products')
    return
  }

  next();
});

export default router
