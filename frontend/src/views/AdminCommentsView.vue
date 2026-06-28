<script>
import axios from "axios";

export default {
  name: "AdminKomentariView",
  data() {
    return {
      komentari: [],
      greska: "",
      poruka: "",
      idZaIzmenu: null,
      tekstZaIzmenu: ""
    };
  },
  methods: {
    authHeaders() {
      const token = localStorage.getItem("token");
      return { Authorization: `Bearer ${token}` };
    },

    async ucitajKomentare() {
      this.greska = "";
      try {
        const res = await axios.get("http://127.0.0.1:5000/admin/comments", {
          headers: this.authHeaders()
        });
        this.komentari = res.data.komentari || [];
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da ucitam komentare";
      }
    },

    zapocniIzmene(komentar) {
      this.poruka = "";
      this.greska = "";
      this.idZaIzmenu = komentar.id;
      this.tekstZaIzmenu = komentar.content;
    },

    prekiniIzmene() {
      this.idZaIzmenu = null;
      this.tekstZaIzmenu = "";
    },

    async sacuvajIzmene(komentar) {
      this.greska = "";
      this.poruka = "";

      if (!this.tekstZaIzmenu.trim()) {
        this.greska = "Komentar ne sme biti prazan!";
        return;
      }

      try {
        await axios.put(
          `http://127.0.0.1:5000/admin/comments/${komentar.id}`,
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

    async obrisiKomentar(komentar) {
      this.poruka = "";
      this.greska = "";
      if (!confirm("Obrisati komentar?")) return;

      try {
        await axios.delete(`http://127.0.0.1:5000/admin/comments/${komentar.id}`, {
          headers: this.authHeaders()
        });

        this.poruka = "Komentar obrisan!";
        await this.ucitajKomentare();
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da obrisem komentar";
      }
    }
  },
  mounted() {
    this.ucitajKomentare();
  }
};
</script>

<template>
  <div class="container mt-4">
    <h3>Admin: Komentari</h3>

    <p class="text-success" v-if="poruka">{{ poruka }}</p>
    <p class="text-danger" v-if="greska">{{ greska }}</p>

    <table class="table table-striped align-middle">
      <thead>
      <tr>
        <th>ID</th>
        <th>Korisnik</th>
        <th>Proizvod</th>
        <th>Komentar</th>
        <th></th>
      </tr>
      </thead>

      <tbody>
      <tr v-for="komentar in komentari" :key="komentar.id">
        <td>{{ komentar.id }}</td>
        <td>{{ komentar.username }}</td>
        <td>{{ komentar.product_name }}</td>

        <td>
          <span v-if="idZaIzmenu !== komentar.id">{{ komentar.content }}</span>

          <div v-else>
            <input v-model="tekstZaIzmenu" class="form-control" />
            <div class="mt-2 d-flex gap-2">
              <button class="btn btn-sm btn-success" @click="sacuvajIzmene(komentar)">Sacuvaj</button>
              <button class="btn btn-sm btn-secondary" @click="prekiniIzmene">Otkazi</button>
            </div>
          </div>
        </td>

        <td class="text-end">
          <div class="d-flex justify-content-end gap-2">
            <button
              v-if="idZaIzmenu !== komentar.id"
              class="btn btn-sm btn-warning"
              @click="zapocniIzmene(komentar)"
            >
              Izmeni
            </button>

            <button
              class="btn btn-sm btn-danger"
              @click="obrisiKomentar(komentar)"
            >
              Obrisi
            </button>
          </div>
        </td>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
</style>
