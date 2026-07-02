<script>
import api from "@/api";

export default {
  name: "LoginView",
  data() {
    return {
      username: "",
      password: "",
      greska: ""
    };
  },
  methods: {
    async login() {
      this.greska = "";

      if (!this.username || !this.password) {
        this.greska = "Username i password su obavezni.";
        return;
      }

      try {
        const res = await api.post("/login", {
          username: this.username,
          password: this.password
        });

        localStorage.setItem("token", res.data.token);
        localStorage.setItem("role", res.data.role);
        localStorage.setItem("username", res.data.username);
        localStorage.setItem("user_id", res.data.user_id);

        const prof = await api.get(
          `/profile/${res.data.username}`,
          { headers: { Authorization: `Bearer ${res.data.token}` } }
        );

        localStorage.setItem("money", prof.data.user.money);
        window.dispatchEvent(new Event("auth-changed"));

        this.$router.push("/products");
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Login neuspesan";
      }
    }
  }
};
</script>

<template>
  <div class="container mt-4" style="max-width: 420px;">
    <h3>Login</h3>

    <div class="mb-2">
      <label class="form-label">Username</label>
      <input class="form-control" v-model="username" />
    </div>

    <div class="mb-2">
      <label class="form-label">Password</label>
      <input class="form-control" type="password" v-model="password" />
    </div>

    <button class="btn btn-primary w-100" @click="login">Uloguj se</button>

    <p class="mt-3 text-center">
      Nemas nalog?
      <RouterLink to="/register">Registruj se</RouterLink>
    </p>

    <p class="text-danger mt-2" v-if="greska">{{ greska }}</p>
  </div>
</template>

<style scoped>
</style>
