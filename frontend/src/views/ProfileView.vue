<script>
import api from "@/api";

export default {
  name: "ProfileView",
  data() {
    return {
      user: null,
      kupovine: [],
      form: {
        email: "",
        godinaRodjenja: "",
        profilnaSlika: "",
        newPassword: ""
      },
      amount: 0,
      loading: true,
      poruka: "",
      greska: ""
    };
  },
  methods: {
    authHeaders() {
      const token = localStorage.getItem("token");
      return { Authorization: `Bearer ${token}` };
    },

    async ucitajProfil() {
      this.loading = true;
      this.greska = "";
      try {
        const username = this.$route.params.username;

        const res = await api.get(`/profile/${username}`, {
          headers: this.authHeaders()
        });

        this.user = res.data.user;
        this.kupovine = res.data.kupovine || [];

        this.form.email = this.user.email || "";
        this.form.godinaRodjenja = this.user.godina_rodjenja || "";
        this.form.profilnaSlika = this.user.profilna_slika || "";
        this.form.newPassword = "";
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da ucitam profil (network/auth).";
      }
      finally {
        this.loading = false;
      }
    },

    async sacuvajProfil() {
      this.greska = "";
      this.poruka = "";

      if (!this.form.email || this.form.godinaRodjenja === "" || !this.form.profilnaSlika) {
        this.greska = "Sva polja (osim lozinke) moraju biti popunjena!";
        return;
      }
      if (Number(this.form.godinaRodjenja) < 1900 || Number(this.form.godinaRodjenja) > 2026) {
        this.greska = "Godina rodjenja nije validna.";
        return;
      }

      try {
        await api.put(
          "/profile/update",
          {
            email: this.form.email,
            godina_rodjenja: Number(this.form.godinaRodjenja),
            profilna_slika: this.form.profilnaSlika,
            password: this.form.newPassword ? this.form.newPassword : null
          },
          { headers: this.authHeaders() }
        );

        this.poruka = "Profil azuriran!";
        await this.ucitajProfil();
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da azuriram profil";
      }
    },

    async dodajNovac() {
      this.greska = "";
      this.poruka = "";

      if (this.amount === "" || Number(this.amount) <= 0) {
        this.greska = "Unesi iznos veci od 0!";
        return;
      }

      try {
        await api.post(
          "/money/add",
          { amount: Number(this.amount) },
          { headers: this.authHeaders() }
        );

        const prof = await api.get(
          `/profile/${localStorage.getItem("username")}`,
          { headers: this.authHeaders() }
        );

        localStorage.setItem("money", prof.data.user.money);
        window.dispatchEvent(new Event("auth-changed"));

        this.poruka = "Novac dodat!";
        this.amount = 0;
        await this.ucitajProfil();
      }
      catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da dodam novac";
      }
    }
  },
  mounted() {
    this.ucitajProfil();
  },
  computed: {
    profilnaSrc() {
      const p = (this.user?.profilna_slika || "").trim()
      if(!p) return ""
      if(p.startsWith("http://") || p.startsWith("https://") || p.startsWith("data:")) return p
      if(p.startsWith("/img/")) return p
      if(p.startsWith("img/")) return "/" + p
      const file = p.split(/[/\\]/).pop()
      return file ? "/img/" + file : ""
    }
  }
};
</script>

<template>
  <div class="container mt-4" v-if="user">
    <h3>Profil: {{ user.username }}</h3>

    <div class="row mt-3">
      <div class="col-md-5">
        <div class="card">
          <div class="card-body">
            <p><b>Email:</b> {{ user.email }}</p>
            <p><b>Godina rođenja:</b> {{ user.godina_rodjenja }}</p>
            <p><b>Uloga:</b> {{ user.role }}</p>
            <p><b>Novac:</b> {{ user.money }}</p>
            <p><b>Profilna slika:</b></p>
            <div v-if="profilnaSrc" class="slika-wrap">
              <img :src="profilnaSrc" alt="">
            </div>
          </div>
        </div>

        <div class="card mt-3">
          <div class="card-body">
            <h5>Dodaj novac</h5>
            <input class="form-control mb-2" type="number" v-model.number="amount" />
            <button class="btn btn-success w-100" @click="dodajNovac">Dodaj</button>
          </div>
        </div>

        <div class="card mt-3">
          <div class="card-body">
            <h5>Izmena profila</h5>

            <div class="mb-2">
              <label class="form-label">Email</label>
              <input class="form-control" v-model="form.email" />
            </div>

            <div class="mb-2">
              <label class="form-label">Godina rođenja</label>
              <input class="form-control" type="number" v-model.number="form.godinaRodjenja" />
            </div>

            <div class="mb-2">
              <label class="form-label">Profilna slika (putanja)</label>
              <input class="form-control" v-model="form.profilnaSlika" />
            </div>

            <div class="mb-3">
              <label class="form-label">Nova lozinka (opciono)</label>
              <input class="form-control" type="password" v-model="form.newPassword" />
            </div>

            <button class="btn btn-primary w-100" @click="sacuvajProfil">
              Sačuvaj izmene
            </button>

            <p class="text-success mt-2" v-if="poruka">{{ poruka }}</p>
            <p class="text-danger mt-2" v-if="greska">{{ greska }}</p>
          </div>
        </div>
      </div>

      <div class="col-md-7">
        <h5>Istorija kupovina</h5>

        <div v-if="kupovine.length === 0" class="text-muted">
          Nema kupovina još uvek.
        </div>

        <table class="table table-striped" v-else>
          <thead>
          <tr>
            <th>Porudzbina</th>
            <th>Datum</th>
            <th>Proizvod</th>
            <th>Kolicina</th>
            <th>Cena</th>
            <th>Ukupno</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="proizvod in kupovine" :key="proizvod.order_id + '-' + proizvod.product_id">
            <td>#{{ proizvod.order_id }}</td>
            <td>{{ proizvod.order_date }}</td>
            <td>{{ proizvod.naziv }}</td>
            <td>{{ proizvod.quantity }}</td>
            <td>{{ proizvod.cena }}</td>
            <td>{{ proizvod.total }}</td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <div class="container mt-4" v-else>
    <div v-if="loading">Ucitavam...</div>
    <div v-else>Ucitavam...</div>
  </div>
</template>

<style scoped>
img{
  max-width: 180px;
  max-height: 180px;
  width: auto;
  height: auto;
  object-fit: cover;
  border-radius: 8px;
}
</style>
