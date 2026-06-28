<script>
import axios from "axios";

export default {
  name: "AdminProductsView",
  data() {
    return {
      proizvodi: [],
      korisnici: [],
      greska: "",
      poruka: "",
      idZaIzmenu: null,
      form: { cena: "", na_stanju: "", popust: "" },
      dodavanjeOtvoreno: false,
      noviProizvod: { naziv: "", opis: "", cena: "", na_stanju: "", popust: 0, seller_id: "" }
    };
  },
  methods: {
    async dodajProizvod() {
      this.$router.push('/products/add')
    },
    async ucitajKorisnike() {
      this.greska = "";
      try {
        const res = await axios.get("http://127.0.0.1:5000/admin/users", {
          headers: this.authHeaders()
        });
        this.korisnici = res.data.users || [];
      } catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || this.greska;
      }
    },
    authHeaders() {
      const token = localStorage.getItem("token");
      return { Authorization: `Bearer ${token}` };
    },
    pronadji_korisnika(id) {
      const user = this.korisnici.find((u) => Number(u.id) === Number(id));
      return user ? user.username : "Ucitavam...";
    },
    async ucitajProizvode() {
      this.greska = "";
      try {
        const res = await axios.get("http://127.0.0.1:5000/admin/products", {
          headers: this.authHeaders()
        });
        this.proizvodi = res.data.products || [];
      } catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da učitam proizvode";
      }
    },
    zapocniIzmene(proizvod) {
      this.idZaIzmenu = proizvod.id;
      this.form.cena = proizvod.cena;
      this.form.na_stanju = proizvod.stock;
      this.form.popust = proizvod.discount_percent ?? 0;
    },
    prekiniIzmene() {
      this.idZaIzmenu = null;
      this.form = { cena: "", na_stanju: "", popust: "" };
    },
    async sacuvajIzmene(id) {
      this.poruka = "";
      this.greska = "";

      if (this.form.cena === "" || this.form.na_stanju === "" || this.form.popust === "") {
        this.greska = "Sva polja moraju biti popunjena!";
        return;
      }
      if (Number(this.form.cena) < 0) {
        this.greska = "Cena mora biti vrednost veca od 0!";
        return;
      }
      if (Number(this.form.na_stanju) < 0) {
        this.greska = "Stanje mora biti vrednost veca od 0!";
        return;
      }
      if (Number(this.form.popust) < 0 || Number(this.form.popust) > 100) {
        this.greska = "Popust mora biti vrednost izmedju 0 i 100!";
        return;
      }

      try {
        await axios.put(
          "http://127.0.0.1:5000/admin/products",
          {
            id: Number(id),
            cena: Number(this.form.cena),
            stock: Number(this.form.na_stanju),
            discount_percent: Number(this.form.popust)
          },
          { headers: this.authHeaders() }
        );

        this.poruka = "Proizvod azuriran!";
        this.prekiniIzmene();
        await this.ucitajProizvode();
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da azuriram proizvod";
      }
    },
    async obrisiProizvod(id) {
      this.poruka = "";
      this.greska = "";
      if (!confirm("Obrisati proizvod?")) return;

      try {
        await axios.delete(`http://127.0.0.1:5000/admin/products/${id}`, {
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
    this.ucitajKorisnike();
  }
};
</script>

<template>
  <div class="container mt-4">
    <h3>Admin: Proizvodi</h3>

    <p class="text-success" v-if="poruka">{{ poruka }}</p>
    <p class="text-danger" v-if="greska">{{ greska }}</p>

    <div class="d-flex justify-content-end mb-3">
      <button class="btn btn-success" @click="dodajProizvod">
        + Dodaj proizvod
      </button>
    </div>

    <table class="table table-striped align-middle">
      <thead>
      <tr>
        <th>ID</th>
        <th>Naziv</th>
        <th>Prodavac</th>
        <th>Cena</th>
        <th>Na stanju</th>
        <th>Popust %</th>
        <th></th>
      </tr>
      </thead>

      <tbody>
      <tr v-for="proizvod in proizvodi" :key="proizvod.id">
        <td>{{ proizvod.id }}</td>
        <td>{{ proizvod.naziv }}</td>
        <td>{{ pronadji_korisnika(proizvod.seller_id) }}</td>

        <td v-if="idZaIzmenu !== proizvod.id">{{ proizvod.cena }}</td>
        <td v-else><input class="form-control" type="number" v-model="form.cena" /></td>

        <td v-if="idZaIzmenu !== proizvod.id">{{ proizvod.stock }}</td>
        <td v-else><input class="form-control" type="number" v-model="form.na_stanju" /></td>

        <td v-if="idZaIzmenu !== proizvod.id">{{ proizvod.discount_percent }}</td>
        <td v-else><input class="form-control" type="number" v-model="form.popust" /></td>

        <td class="text-end">
          <button v-if="idZaIzmenu !== proizvod.id" class="btn btn-sm btn-primary me-2" @click="zapocniIzmene(proizvod)">Edit</button>
          <button v-else class="btn btn-sm btn-success me-2" @click="sacuvajIzmene(proizvod.id)">Save</button>
          <button v-if="idZaIzmenu === proizvod.id" class="btn btn-sm btn-secondary me-2" @click="prekiniIzmene">Cancel</button>
          <button class="btn btn-sm btn-danger" @click="obrisiProizvod(proizvod.id)">Delete</button>
        </td>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
</style>
