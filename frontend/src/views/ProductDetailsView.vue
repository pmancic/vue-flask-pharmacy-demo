<script>
import axios from "axios";

export default {
  name: "ProductDetailsView",
  data() {
    return {
      proizvod: null,
      komentari: [],
      noviKomentar: "",
      greska: "",
      poruka: "",
      role: localStorage.getItem("role"),
      userId: Number(localStorage.getItem("user_id")),

      idZaIzmenu: null,
      tekstZaIzmenu: "",

      dodajKolicinu: 0,
      loadingStock: false
    };
  },
  computed: {
    isSellerOfThisProduct() {
      return (
        this.role === "prodavac" &&
        this.proizvod &&
        Number(this.proizvod.seller_id) === this.userId
      );
    },
    mozeDodatiStanje() {
      return this.role === "administrator" || this.isSellerOfThisProduct;
    }
  },
  methods: {
    authHeaders() {
      const token = localStorage.getItem("token");
      return { Authorization: `Bearer ${token}` };
    },

    mozeMenjatiKomentar(komentar) {
      return (
        this.role === "administrator" ||
        Number(komentar.user_id) === this.userId ||
        this.isSellerOfThisProduct
      );
    },

    async ucitajProizvod() {
      this.greska = "";
      try {
        const id = Number(this.$route.params.id);
        const res = await axios.get("http://127.0.0.1:5000/products", {
          headers: this.authHeaders()
        });
        const lista = res.data.products || [];
        this.proizvod = lista.find(p => Number(p.id) === id);

        if (!this.proizvod) {
          this.greska = "Proizvod nije pronadjen.";
        }
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da ucitam proizvod";
      }
    },

    async ucitajKomentare() {
      this.greska = "";
      try {
        const id = this.$route.params.id;
        const res = await axios.get(`http://127.0.0.1:5000/products/${id}/comments`);
        this.komentari = res.data.comments || [];
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da ucitam komentare";
      }
    },

    async dodajKomentar() {
      this.greska = "";
      this.poruka = "";

      if (!this.noviKomentar.trim()) return;

      try {
        await axios.post(
          `http://127.0.0.1:5000/products/${this.proizvod.id}/comment`,
          { content: this.noviKomentar },
          { headers: this.authHeaders() }
        );
        this.noviKomentar = "";
        this.poruka = "Komentar dodat!";
        await this.ucitajKomentare();
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Greska pri dodavanju komentara";
      }
    },

    async obrisiProizvod(id) {
      this.poruka = "";
      this.greska = "";
      if (!confirm("Obrisati proizvod?")) return;

      try {
        await axios.delete(`http://127.0.0.1:5000/products/delete/${id}`, {
          headers: this.authHeaders()
        });
        this.poruka = "Proizvod obrisan!";
        await this.ucitajProizvode();
      } catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da obrisem proizvod";
      }
    },

    async obrisiKomentar(id) {
      this.greska = "";
      this.poruka = "";

      try {
        await axios.delete(
          `http://127.0.0.1:5000/products/${this.proizvod.id}/comment/delete/${id}`,
          { headers: this.authHeaders() }
        );
        this.poruka = "Komentar obrisan!";
        await this.ucitajKomentare();
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da obrisem komentar";
      }
    },

    mozeMenjati(proizvod) {
      return (
        this.role === "administrator" ||
        (this.role === "prodavac" && Number(proizvod.seller_id) === this.userId)
      );
    },

    async dodajUKorpu(product_id) {
      this.poruka = "";
      this.greska = "";

      try {
        await axios.post(`http://127.0.0.1:5000/cart/add/${product_id}`, {}, {
          headers: this.authHeaders()
        });
        this.poruka = "Dodato u korpu!";
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da dodam u korpu";
      }
    },

    zapocniIzmene(komentar) {
      this.greska = "";
      this.poruka = "";
      this.idZaIzmenu = komentar.id;
      this.tekstZaIzmenu = komentar.content;
    },

    prekiniIzmene() {
      this.idZaIzmenu = null;
      this.tekstZaIzmenu = "";
    },

    async sacuvajIzmeneKomentara(id) {
      this.greska = "";
      this.poruka = "";

      if (!this.tekstZaIzmenu.trim()) return;

      try {
        await axios.put(
          `http://127.0.0.1:5000/products/${this.proizvod.id}/comment/update/${id}`,
          { content: this.tekstZaIzmenu },
          { headers: this.authHeaders() }
        );
        this.poruka = "Komentar izmenjen!";
        this.prekiniIzmene();
        await this.ucitajKomentare();
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da izmenim komentar";
      }
    },

    async dodajNaStanje() {
      this.greska = "";
      this.poruka = "";

      if (!this.mozeDodatiStanje) {
        this.greska = "Nemate dozvolu da dodajete na stanje.";
        return;
      }

      const kolicina = Number(this.dodajKolicinu);
      if (!kolicina || kolicina <= 0) {
        this.greska = "Unesi kolicinu vecu od 0.";
        return;
      }

      this.loadingStock = true;
      try {
        await axios.put(
          `http://127.0.0.1:5000/products/update/${this.proizvod.id}`,
          { stock: Number(this.proizvod.stock) + kolicina },
          { headers: this.authHeaders() }
        );

        this.proizvod.stock = Number(this.proizvod.stock) + kolicina;
        this.dodajKolicinu = 0;
        this.poruka = "Stanje azurirano!";
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Greska pri dodavanju na stanje";
      }
      finally {
        this.loadingStock = false;
      }
    }
  },
  async mounted() {
    await this.ucitajProizvod();
    await this.ucitajKomentare();
  }
};
</script>

<template>
  <div class="container mt-4" v-if="proizvod">
    <h3>{{ proizvod.naziv }}</h3>
    <p>Cena: {{ proizvod.cena }}</p>
    <p>Na stanju: {{ proizvod.stock }}</p>
    <p>{{ proizvod.opis }}</p>
    <div class="d-flex gap-2 justify-content-center">
      <button class="btn btn-success" v-if='role === "kupac"' @click="dodajUKorpu(proizvod.id)">Dodaj u korpu</button>
      <button v-if="mozeMenjati(proizvod)" type="button" class="btn btn-warning" data-bs-dismiss="modal" @click="$router.push(`/products/edit/${proizvod.id}`)">Izmeni</button>
      <button v-if="mozeMenjati(proizvod)" type="button" class="btn btn-danger" data-bs-dismiss="modal" @click="obrisiProizvod(proizvod.id)">Obrisi</button>
      <button class="btn btn-secondary" data-bs-dismiss="modal" @click="this.$router.push('/products')">Nazad</button>
    </div>

    <div v-if="mozeDodatiStanje" class="mt-3">
      <div class="d-flex gap-2 align-items-end" style="max-width: 420px;">
        <div class="flex-grow-1">
          <label class="form-label">Dodaj na stanje</label>
          <input class="form-control" type="number" min="1" v-model="dodajKolicinu" />
        </div>
        <button class="btn btn-success" :disabled="loadingStock" @click="dodajNaStanje">
          {{ loadingStock ? "Dodajem..." : "Dodaj" }}
        </button>
      </div>
    </div>

    <p class="text-success mt-2" v-if="poruka">{{ poruka }}</p>
    <p class="text-danger mt-2" v-if="greska">{{ greska }}</p>

    <hr />

    <h5>Komentari</h5>

    <div v-if="komentari.length === 0" class="text-muted">
      Nema komentara.
    </div>

    <ul class="list-group mb-3">
      <li v-for="komentar in komentari" :key="komentar.id" class="list-group-item d-flex justify-content-between align-items-start">
        <div class="flex-grow-1 me-2">
          <strong>{{ komentar.username }}</strong>:

          <span v-if="idZaIzmenu !== komentar.id">
            {{ komentar.content }}
          </span>

          <div v-else class="mt-2">
            <input v-model="tekstZaIzmenu" class="form-control" />
            <div class="mt-2 d-flex gap-2">
              <button class="btn btn-sm btn-success" @click="sacuvajIzmeneKomentara(komentar.id)">Sacuvaj</button>
              <button class="btn btn-sm btn-secondary" @click="prekiniIzmene">Otkazi</button>
            </div>
          </div>
        </div>

        <div class="d-flex gap-2">
          <button
            v-if="mozeMenjatiKomentar(komentar) && idZaIzmenu !== komentar.id"
            class="btn btn-sm btn-warning"
            @click="zapocniIzmene(komentar)"
          >
            Izmeni
          </button>

          <button v-if="mozeMenjatiKomentar(komentar)" class="btn btn-sm btn-danger" @click="obrisiKomentar(komentar.id)">
            Obrisi
          </button>
        </div>
      </li>
    </ul>

    <div class="input-group">
      <input v-model="noviKomentar" class="form-control" placeholder="Dodaj komentar" />
      <button class="btn btn-primary" @click="dodajKomentar">Posalji</button>
    </div>
  </div>
</template>

<style scoped>
</style>
