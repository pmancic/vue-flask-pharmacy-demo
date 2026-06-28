<script>
import axios from "axios";

export default {
  name: "EditProductView",
  data() {
    return {
      id: null,
      proizvod: null,

      naziv: "",
      opis: "",
      cena: "",
      na_stanju: "",
      popust: 0,

      greska: "",
      poruka: "",
      loading: true,
      saving: false
    };
  },
  computed: {
    role() {
      return localStorage.getItem("role");
    },
    userId() {
      return Number(localStorage.getItem("user_id"));
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

    async ucitajProizvod() {
      this.greska = "";
      this.poruka = "";
      this.loading = true;

      try {
        const res = await axios.get("http://127.0.0.1:5000/products", {
          headers: this.authHeaders()
        });
        const lista = res.data.products || [];
        const p = lista.find(x => Number(x.id) === Number(this.id));

        if (!p) {
          this.greska = "Proizvod ne postoji.";
          return;
        }

        if (!this.proveraProdavaciliAdmin) {
          this.greska = "Nemate dozvolu.";
          return;
        }

        if (this.role !== "administrator" && Number(p.seller_id) !== this.userId) {
          this.greska = "Možete menjati samo svoje proizvode.";
          return;
        }

        this.proizvod = p;
        this.naziv = p.naziv || "";
        this.opis = p.opis || "";
        this.cena = (p.cena ?? "").toString();
        this.na_stanju = (p.stock ?? 0).toString();
        this.popust = Number(p.discount_percent ?? 0);
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Greska pri ucitavanju";
      }
      finally {
        this.loading = false;
      }
    },

    async sacuvajIzmene() {
      this.greska = "";
      this.poruka = "";
      this.saving = true;

      if (!this.naziv || !this.opis || this.cena === "" || this.na_stanju === "" || this.popust === "") {
        this.greska = "Sva polja moraju biti popunjena!";
        this.saving = false;
        return;
      }
      if (Number(this.cena) < 0) {
        this.greska = "Cena mora biti vrednost veca od 0!";
        this.saving = false;
        return;
      }
      if (Number(this.na_stanju) < 0) {
        this.greska = "Stanje mora biti vrednost veca od 0!";
        this.saving = false;
        return;
      }
      if (Number(this.popust) < 0 || Number(this.popust) > 100) {
        this.greska = "Popust mora biti vrednost izmedju 0 i 100!";
        this.saving = false;
        return;
      }

      try {
        await axios.put(
          `http://127.0.0.1:5000/products/update/${this.id}`,
          {
            naziv: this.naziv,
            opis: this.opis,
            cena: Number(this.cena),
            stock: Number(this.na_stanju),
            discount_percent: Number(this.popust)
          },
          { headers: this.authHeaders() }
        );

        this.poruka = "Proizvod azuriran!";
        this.$router.push("/products");
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Greska pri cuvanju";
      }
      finally {
        this.saving = false;
      }
    }
  },
  mounted() {
    this.id = this.$route.params.id;
    this.ucitajProizvod();
  }
};
</script>

<template>
  <div class="container mt-4" style="max-width: 650px;">
    <h3>Izmeni proizvod</h3>

    <p class="text-success" v-if="poruka">{{ poruka }}</p>

    <div v-if="loading">Ucitavam...</div>
    <p class="text-danger" v-else-if="greska">{{ greska }}</p>

    <div v-else>
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

      <button class="btn btn-primary w-100" :disabled="saving" @click="sacuvajIzmene">
        {{ saving ? "Cuvam..." : "Sacuvaj izmene" }}
      </button>

      <p class="text-danger mt-2" v-if="greska">{{ greska }}</p>
    </div>
  </div>
</template>

<style scoped>
</style>
