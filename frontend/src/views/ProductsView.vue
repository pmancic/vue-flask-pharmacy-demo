<script>
import api from "@/api";

export default {
  name: "ProductsView",
  data() {
    return {
      proizvodi: [],
      greska: "",
      poruka: ""
    };
  },

  computed: {
    role() {
      return localStorage.getItem("role");
    },
    userId() {
      return Number(localStorage.getItem("user_id"));
    },
    isProdavacIliAdmin() {
      return this.role === "prodavac" || this.role === "administrator";
    }
  },

  methods: {
    authHeaders() {
      const token = localStorage.getItem("token");
      return { Authorization: `Bearer ${token}` };
    },

    async ucitajProizvode() {
      this.greska = "";
      try {
        const res = await api.get("/products", {
          headers: this.authHeaders()
        });
        this.proizvodi = res.data.products || [];
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da ucitam proizvode";
      }
    },

    mozeMenjati(proizvod) {
      if (!this.isProdavacIliAdmin) return false;
      if (this.role === "administrator") return true;
      return Number(proizvod.seller_id) === this.userId;
    },

    async dodajUKorpu(product_id) {
      this.poruka = "";
      this.greska = "";

      try {
        await api.post(`/cart/add/${product_id}`, {}, {
          headers: this.authHeaders()
        });
        this.poruka = "Dodato u korpu!";
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da dodam u korpu";
      }
    },

    async obrisiProizvod(id) {
      this.poruka = "";
      this.greska = "";
      if (!confirm("Obrisati proizvod?")) return;

      try {
        await api.delete(`/products/delete/${id}`, {
          headers: this.authHeaders()
        });
        this.poruka = "Proizvod obrisan!";
        await this.ucitajProizvode();
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da obrisem proizvod";
      }
    }
  },

  mounted() {
    this.ucitajProizvode();
  }
};
</script>

<template>
  <div>
    <h1>Dobrodosli! Ovo su nasi proizvodi!</h1>

    <p class="text-success" v-if="poruka">{{ poruka }}</p>
    <p class="text-danger" v-if="greska">{{ greska }}</p>

    <div class="row">
      <div class="d-flex flex-wrap gap-5 p-2">
        <div class="card" style="width: 20rem;" v-for="proizvod in proizvodi" :key="proizvod.id">
          <div class="card-body">
            <h5 class="card-title">{{proizvod.naziv}}</h5>
            <p class="card-text">{{proizvod.opis}}</p>
          </div>

          <button type="button" class="btn btn-primary" data-bs-toggle="modal" :data-bs-target="'#staticBackdrop'+proizvod.id">
            Prikazi detaljnije
          </button>

          <div class="modal fade" :id="'staticBackdrop'+proizvod.id" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog">
              <div class="modal-content">
                <div class="modal-header d-flex gap-2">
                  <h1 class="modal-title fs-5">{{ proizvod.naziv }}</h1>
                  <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>

                <div class="modal-body">
                  <p>{{proizvod.opis}}</p>
                  <p>Prodavac: {{ proizvod.seller_username || "-" }}</p>
                  <p>Cena: {{proizvod.cena}}</p>
                  <p>Na stanju: {{ proizvod.stock }}</p>
                  <p v-if="proizvod.discount_percent > 0">Popust: {{ proizvod.discount_percent }}%</p>
                </div>

                <div class="modal-footer">
                  <button class="btn btn-success" v-if='role === "kupac"' @click="dodajUKorpu(proizvod.id)">Dodaj u korpu</button>
                  <button type="button" class="btn btn-outline-info" data-bs-dismiss="modal" @click="$router.push(`/products/${proizvod.id}`)">Link ka stranici proizvoda</button>
                  <button v-if="mozeMenjati(proizvod)" type="button" class="btn btn-danger" data-bs-dismiss="modal" @click="obrisiProizvod(proizvod.id)">Obrisi</button>
                  <button v-if="mozeMenjati(proizvod)" type="button" class="btn btn-warning" data-bs-dismiss="modal" @click="$router.push(`/products/edit/${proizvod.id}`)">Izmeni</button>
                  <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zatvori</button>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
