<script>
import axios from "axios";

export default {
  name: "CartView",
  data() {
    return {
      proizvodi: [],
      total: "0.00",
      greska: "",
      poruka: "",
      loading: false
    };
  },
  methods: {
    authHeaders() {
      const token = localStorage.getItem("token");
      return { Authorization: `Bearer ${token}` };
    },

    async ucitajKorpu() {
      this.loading = true;
      this.greska = "";
      try {
        const res = await axios.get("http://127.0.0.1:5000/cart", {
          headers: this.authHeaders()
        });
        this.proizvodi = res.data.items || [];
        this.total = res.data.total ?? "0.00";
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da ucitam korpu";
      }
      finally {
        this.loading = false;
      }
    },

    async promeniKolicinu(productId, quantity) {
      this.greska = "";
      this.poruka = "";

      if (quantity === "" || Number(quantity) <= 0) {
        this.greska = "Kolicina mora biti vrednost veca od 0!";
        return;
      }

      try {
        await axios.put(
          `http://127.0.0.1:5000/cart/update/${productId}`,
          { quantity: Number(quantity) },
          { headers: this.authHeaders() }
        );
        await this.ucitajKorpu();
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da azuriram kolicinu";
      }
    },

    async obrisiIzKorpe(productId) {
      this.greska = "";
      this.poruka = "";

      try {
        await axios.delete(`http://127.0.0.1:5000/cart/delete/${productId}`, {
          headers: this.authHeaders()
        });
        await this.ucitajKorpu();
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da obrisem proizvod";
      }
    },

    async zavrsiKupovinu() {
      this.greska = "";
      this.poruka = "";
      this.loading = true;

      try {
        const res = await axios.post(
          "http://127.0.0.1:5000/checkout",
          {},
          { headers: this.authHeaders() }
        );

        if (res?.data?.new_money != null) {
          localStorage.setItem("money", res.data.new_money);
          window.dispatchEvent(new Event("auth-changed"));
        }

        this.poruka = "Kupovina uspesna!";
        await this.ucitajKorpu();
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Kupovina neuspesna";
      }
      finally {
        this.loading = false;
      }
    }
  },
  mounted() {
    this.ucitajKorpu();
  }
};
</script>

<template>
  <div class="container mt-4">
    <h3>Korpa</h3>

    <div v-if="loading">Ucitavam...</div>

    <div v-else>
      <p class="text-danger" v-if="greska">{{ greska }}</p>
      <p class="text-success" v-if="poruka">{{ poruka }}</p>

      <div v-if="proizvodi.length === 0" class="text-muted">
        Korpa je prazna.
      </div>

      <div v-else>
        <table class="table table-striped align-middle">
          <thead>
          <tr>
            <th>Proizvod</th>
            <th>Cena bez popusta</th>
            <th>Cena sa popustom</th>
            <th>Kolicina</th>
            <th>Ukupno</th>
            <th></th>
          </tr>
          </thead>

          <tbody>
          <tr v-for="proizvod in proizvodi" :key="proizvod.product_id">
            <td>{{ proizvod.naziv }}</td>
            <td>{{ proizvod.cena }}</td>
            <td>{{ proizvod.unit_price }}</td>

            <td style="max-width: 150px;">
              <input
                class="form-control"
                type="number"
                min="1"
                :max="proizvod.stock"
                :value="proizvod.quantity"
                @change="promeniKolicinu(proizvod.product_id, $event.target.value)"
              />
              <small class="text-muted">Na stanju: {{ proizvod.stock }}</small>
            </td>

            <td>{{ proizvod.line_total }}</td>

            <td>
              <button class="btn btn-danger btn-sm" @click="obrisiIzKorpe(proizvod.product_id)">
                Obrisi
              </button>
            </td>
          </tr>
          </tbody>
        </table>

        <div class="d-flex justify-content-between align-items-center">
          <h5>Total: {{ total }}</h5>
          <button class="btn btn-success" :disabled="proizvodi.length === 0 || loading" @click="zavrsiKupovinu">
            Obavi kupovinu
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
