<script>
import api from "@/api";

export default {
  name: "AddProductView",
  data() {
    return {
      naziv: "",
      opis: "",
      cena: "",
      na_stanju: "",
      popust: 0,

      prodavci: [],
      prodavac_id: "",
      isAdmin: false,

      greska: "",
      poruka: "",
      loading: false
    };
  },
  computed: {
    role() {
      return localStorage.getItem("role");
    },
    proveraProdavaciliAdmin() {
      return this.role === "prodavac" || this.role === "administrator";
    }
  },
  methods: {
    authHeaders() {
      const token = localStorage.getItem("token");
      return { Authorization: `Bearer ${token}` };
    },

    async ucitajProdavce() {
      this.greska = "";
      try {
        const res = await api.get("/admin/users", {
          headers: this.authHeaders()
        });
        const lista = res.data.users || [];
        this.prodavci = lista.filter(x => x.role === "prodavac");
      }
      catch (e) {
        this.prodavci = [];
      }
    },

    async dodajProizvod() {
      this.poruka = "";
      this.greska = "";

      if (!this.proveraProdavaciliAdmin) {
        this.greska = "Nemate dozvolu da dodajete proizvode.";
        return;
      }

      if (!this.naziv || !this.opis || this.cena === "" || this.na_stanju === "" || this.popust === "") {
        this.greska = "Sve polja moraju biti popunjena!";
        return;
      }
      else if (Number(this.cena) < 0) {
        this.greska = "Cena mora biti vrednost veca od 0!";
        return;
      }
      else if (Number(this.na_stanju) < 0) {
        this.greska = "Stanje mora biti vrednost veca od 0!";
        return;
      }
      else if (Number(this.popust) < 0 || Number(this.popust) > 100) {
        this.greska = "Popust mora biti vrednost izmedju 0 i 100!";
        return;
      }

      if (this.isAdmin && !this.prodavac_id) {
        this.greska = "Admin mora izabrati prodavca.";
        return;
      }

      this.loading = true;
      try {
        const payload = {
          naziv: this.naziv,
          opis: this.opis,
          cena: Number(this.cena),
          stock: Number(this.na_stanju),
          discount_percent: Number(this.popust)
        };

        if (this.isAdmin) {
          payload.seller_id = Number(this.prodavac_id);
        }

        await api.post("/products/add", payload, {
          headers: this.authHeaders()
        });

        this.poruka = "Proizvod dodat!";
        this.$router.push("/products");
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da dodam proizvod";
      }
      finally {
        this.loading = false;
      }
    }
  },
  mounted() {
    this.isAdmin = this.role === "administrator";
    if (this.isAdmin) this.ucitajProdavce();
  }
};
</script>

<template>
  <div class="container mt-4" style="max-width: 650px;">
    <h3>Dodaj proizvod</h3>

    <p class="text-success" v-if="poruka">{{ poruka }}</p>
    <p class="text-danger" v-if="greska">{{ greska }}</p>

    <div v-if="isAdmin" class="mb-2">
      <label class="form-label">Prodavac</label>
      <select class="form-select" v-model="prodavac_id">
        <option value="">Prodavac...</option>
        <option v-for="u in prodavci" :key="u.id" :value="u.id">{{ u.username }}</option>
      </select>
    </div>

    <div class="mb-2">
      <label class="form-label">Naziv</label>
      <input class="form-control" v-model="naziv" />
    </div>

    <div class="mb-2">
      <label class="form-label">Opis</label>
      <textarea class="form-control" rows="3" v-model="opis"></textarea>
    </div>

    <div class="mb-2">
      <label class="form-label">Cena</label>
      <input class="form-control" type="number" step="0.01" v-model="cena" />
    </div>

    <div class="mb-2">
      <label class="form-label">Na stanju</label>
      <input class="form-control" type="number" v-model="na_stanju" />
    </div>

    <div class="mb-3">
      <label class="form-label">Popust (%)</label>
      <input class="form-control" type="number" v-model="popust" />
    </div>

    <button class="btn btn-success w-100" :disabled="loading" @click="dodajProizvod">
      {{ loading ? "Dodajem..." : "Dodaj proizvod" }}
    </button>
  </div>
</template>

<style scoped>
</style>
