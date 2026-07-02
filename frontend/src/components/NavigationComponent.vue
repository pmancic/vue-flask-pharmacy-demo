<script>
export default {
  name: "NavigationComponent",
  data() {
    return {
      role: localStorage.getItem("role"),
      username: localStorage.getItem("username"),
      token: localStorage.getItem("token"),
      tick: 0
    };
  },
  computed: {
    proveraUlogovan() {
      return !!this.token;
    },
    proveraProdavac() {
      return this.role === "prodavac";
    },
    moneyValue() {
      this.tick;
      const m = localStorage.getItem("money");
      return m !== null ? Number(m) : 0;
    }
  },
  mounted() {
    window.addEventListener("auth-changed", this.syncAuth);
  },
  beforeUnmount() {
    window.removeEventListener("auth-changed", this.syncAuth);
  },
  methods: {
    syncAuth() {
      this.role = localStorage.getItem("role");
      this.username = localStorage.getItem("username");
      this.token = localStorage.getItem("token");
      this.tick++;
    },
    profil() {
      this.$router.push("/profile/" + this.username);
    },
    logout() {
      localStorage.removeItem("token");
      localStorage.removeItem("role");
      localStorage.removeItem("username");
      localStorage.removeItem("user_id");
      localStorage.removeItem("money");
      window.dispatchEvent(new Event("auth-changed"));
      this.$router.push("/login");
    }
  }
};
</script>

<template>
  <nav class="navbar navbar-expand-lg bg-body-tertiary">
    <div class="container-fluid d-flex">
      <RouterLink class="navbar-brand" to="/">PharmaShop</RouterLink>

      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto">
          <li class="nav-item" v-if="role != 'administrator' && proveraUlogovan">
            <RouterLink class="nav-link" to="/products">Proizvodi</RouterLink>
          </li>

          <li v-if="role === 'administrator'">
            <RouterLink class="nav-link" to="/admin/products">Admin proizvodi</RouterLink>
          </li>

          <li class="nav-item" v-if="proveraProdavac">
            <RouterLink class="nav-link" to="/products/add">Dodaj proizvod</RouterLink>
          </li>

          <li v-if="proveraUlogovan && role !== 'administrator' && role !== 'prodavac'">
            <RouterLink class="nav-link" to="/cart">Korpa</RouterLink>
          </li>

          <li v-if="role === 'administrator'">
            <RouterLink class="nav-link" to="/admin/users">Admin panel</RouterLink>
          </li>
          <li v-if="role === 'administrator'">
            <RouterLink class="nav-link" to="/admin/comments">Admin komentari</RouterLink>
          </li>
        </ul>

        <ul class="navbar-nav ms-auto align-items-center gap-4">
          <li v-if="proveraUlogovan && role != 'administrator'" class="nav-item">
            <span class="nav-link fw-semibold">{{ moneyValue }} RSD</span>
          </li>

          <li class="nav-item dropdown" v-if="proveraUlogovan">
            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
              {{ username }}
            </a>
            <ul class="dropdown-menu dropdown-menu-end">
              <li>
                <button class="dropdown-item" @click="profil">Moj profil</button>
              </li>
              <li>
                <button class="dropdown-item" @click="logout">Logout</button>
              </li>
            </ul>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<style scoped>
li {
  list-style: none;
}
</style>
