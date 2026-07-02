<script>
import api from "@/api";

export default {
  name: "AdminAddUserView",
  data() {
    return {
      username: "",
      password: "",
      email: "",
      godina_rodjenja: "",
      profilna_slika: "",
      role: "kupac",

      greska: "",
      poruka: "",
      loading: false
    };
  },
  computed: {
    roleUlogovanog() {
      return localStorage.getItem("role");
    },
    isAdmin() {
      return this.roleUlogovanog === "administrator";
    }
  },
  methods: {
    authHeaders() {
      const token = localStorage.getItem("token");
      return { Authorization: `Bearer ${token}` };
    },

    async dodajKorisnika() {
      this.poruka = "";
      this.greska = "";

      if (!this.isAdmin) {
        this.greska = "Nemate dozvolu da dodajete korisnike.";
        return;
      }

      if (
        !this.username ||
        !this.password ||
        !this.email ||
        this.godina_rodjenja === "" ||
        !this.role
      ) {
        this.greska = "Sva polja sem profilne slike moraju biti popunjena!";
        return;
      }

      const g = Number(this.godina_rodjenja);
      if (!Number.isInteger(g) || g < 1900 || g > 2026) {
        this.greska = "Godina rodjenja nije validna!";
        return;
      }

      this.loading = true;
      try {
        await api.post(
          "/admin/users/add",
          {
            username: this.username,
            password: this.password,
            email: this.email,
            godina_rodjenja: g,
            profilna_slika: this.profilna_slika,
            role: this.role
          },
          { headers: this.authHeaders() }
        );

        this.poruka = "Korisnik dodat!";
        this.$router.push("/admin/users");
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da dodam korisnika";
      }
      finally {
        this.loading = false;
      }
    }
  },
  mounted() {
    if (!this.isAdmin) this.$router.push("/products");
  }
};
</script>

<template>
  <div class="container mt-4" style="max-width: 650px;">
    <h3>Dodaj korisnika</h3>

    <p class="text-success" v-if="poruka">{{ poruka }}</p>
    <p class="text-danger" v-if="greska">{{ greska }}</p>

    <div class="mb-2">
      <label class="form-label">Username</label>
      <input class="form-control" v-model="username" />
    </div>

    <div class="mb-2">
      <label class="form-label">Password</label>
      <input class="form-control" type="password" v-model="password" />
    </div>

    <div class="mb-2">
      <label class="form-label">Email</label>
      <input class="form-control" v-model="email" />
    </div>

    <div class="mb-2">
      <label class="form-label">Godina rodjenja</label>
      <input class="form-control" type="number" v-model="godina_rodjenja" />
    </div>

    <div class="mb-2">
      <label class="form-label">Profilna slika</label>
      <input class="form-control" v-model="profilna_slika" />
    </div>

    <div class="mb-3">
      <label class="form-label">Uloga</label>
      <select class="form-select" v-model="role">
        <option value="kupac">kupac</option>
        <option value="prodavac">prodavac</option>
        <option value="administrator">administrator</option>
      </select>
    </div>

    <button class="btn btn-success w-100" :disabled="loading" @click="dodajKorisnika">
      {{ loading ? "Dodajem..." : "Dodaj korisnika" }}
    </button>
  </div>
</template>

<style scoped>
</style>
