<script>
import axios from "axios";

export default {
  name: "RegisterView",
  data() {
    return {
      username: "",
      email: "",
      password: "",
      godinaRodjenja: "",
      profilnaSlika: "",
      role: "kupac",
      greska: "",
      poruka: ""
    };
  },
  methods: {
    async register() {
      this.greska = "";
      this.poruka = "";

      if (!this.username || !this.email || !this.password || this.godinaRodjenja === "") {
        this.greska = "Sva polja sem profilne slike moraju biti popunjena!";
        return;
      }
      if (Number(this.godinaRodjenja) < 1900 || Number(this.godinaRodjenja) > 2026) {
        this.greska = "Godina rodjenja nije validna.";
        return;
      }

      try {
        await axios.post("http://127.0.0.1:5000/register", {
          username: this.username,
          password: this.password,
          email: this.email,
          godinaRodjenja: Number(this.godinaRodjenja),
          profilnaSlika: this.profilnaSlika,
          role: this.role
        });

        const res = await axios.post("http://127.0.0.1:5000/login", {
          username: this.username,
          password: this.password
        });

        localStorage.setItem("token", res.data.token);
        localStorage.setItem("role", res.data.role);
        localStorage.setItem("username", res.data.username);
        localStorage.setItem("user_id", res.data.user_id);

        const prof = await axios.get(
          `http://127.0.0.1:5000/profile/${res.data.username}`,
          { headers: { Authorization: `Bearer ${res.data.token}` } }
        );

        localStorage.setItem("money", prof.data.user.money);
        window.dispatchEvent(new Event("auth-changed"));

        this.$router.push("/products");
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Registracija neuspesna";
      }
    }
  }
};
</script>

<template>
  <div class="container mt-4" style="max-width: 520px;">
    <h3>Registracija</h3>

    <div class="mb-2">
      <label class="form-label">Username</label>
      <input class="form-control" v-model="username" />
    </div>

    <div class="mb-2">
      <label class="form-label">Email</label>
      <input class="form-control" v-model="email" />
    </div>

    <div class="mb-2">
      <label class="form-label">Password</label>
      <input class="form-control" type="password" v-model="password" />
    </div>

    <div class="mb-2">
      <label class="form-label">Godina rodjenja</label>
      <input class="form-control" type="number" v-model="godinaRodjenja" />
    </div>

    <div class="mb-2">
      <label class="form-label">Profilna slika (putanja)</label>
      <input class="form-control" v-model="profilnaSlika" placeholder="npr. img/user.png" />
    </div>

    <div class="mb-3">
      <label class="form-label">Vrsta korisnika</label>
      <select class="form-select" v-model="role">
        <option value="kupac">Kupac</option>
        <option value="prodavac">Prodavac</option>
      </select>
    </div>

    <button class="btn btn-success w-100" @click="register">Registruj se</button>

    <p class="text-danger mt-2" v-if="greska">{{ greska }}</p>
    <p class="text-success mt-2" v-if="poruka">{{ poruka }}</p>
  </div>
</template>

<style scoped>
</style>
