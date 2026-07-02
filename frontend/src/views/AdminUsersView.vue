<script>
import api from "@/api"

export default {
  name: "AdminUsersView",
  data() {
    return {
      users: [],
      greska: "",
      poruka: "",

      idZaIzmenu: null,
      form: {
        username: "",
        email: "",
        godina_rodjenja: "",
        profilna_slika: "",
        role: "kupac",
        money: "",
        password: "",
        password2: ""
      }
    }
  },
  methods: {
    authHeaders() {
      const token = localStorage.getItem("token")
      return { Authorization: `Bearer ${token}` }
    },

    async loadUsers() {
      this.greska = ""
      try {
        const res = await api.get("/admin/users", {
          headers: this.authHeaders()
        })
        this.users = res.data?.users || res.data || []
      } catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da ucitam korisnike"
      }
    },

    startEdit(u) {
      this.poruka = ""
      this.greska = ""
      this.idZaIzmenu = u.id

      this.form.username = u.username ?? ""
      this.form.email = u.email ?? ""
      this.form.godina_rodjenja = u.godina_rodjenja ?? ""
      this.form.profilna_slika = u.profilna_slika ?? ""
      this.form.role = u.role ?? "kupac"
      this.form.money = u.money ?? 0

      this.form.password = ""
      this.form.password2 = ""
    },

    cancelEdit() {
      this.idZaIzmenu = null
      this.form = {
        username: "",
        email: "",
        godina_rodjenja: "",
        profilna_slika: "",
        role: "kupac",
        money: "",
        password: "",
        password2: ""
      }
    },

    validacija() {
      if (
        !this.form.username ||
        !this.form.email ||
        this.form.godina_rodjenja === "" ||
        !this.form.profilna_slika ||
        !this.form.role ||
        this.form.money === ""
      ) {
        return "Sva polja (osim password-a) moraju biti popunjena!"
      }

      const yr = Number(this.form.godina_rodjenja)
      const now = new Date().getFullYear()
      if (!Number.isInteger(yr) || yr < 1900 || yr > now) {
        return "Godina rodjenja nije validna!"
      }

      const m = Number(this.form.money)
      if (Number.isNaN(m) || m < 0) {
        return "Novac mora biti broj veci ili jednak 0!"
      }

      if (!this.form.email.includes("@") || !this.form.email.includes(".")) {
        return "Email nije validan!"
      }

      if (this.form.password || this.form.password2) {
        if (this.form.password.length < 6) return "Password mora imati bar 4 karaktera!"
        if (this.form.password !== this.form.password2) return "Password potvrda se ne poklapa!"
      }

      return ""
    },

    async sacuvajIzmene(id) {
      this.poruka = ""
      this.greska = ""

      const err = this.validacija()
      if (err) {
        this.greska = err
        return
      }

      const payload = {
        username: this.form.username.trim(),
        email: this.form.email.trim(),
        godina_rodjenja: Number(this.form.godina_rodjenja),
        profilna_slika: this.form.profilna_slika.trim(),
        role: this.form.role,
        money: Number(this.form.money)
      }

      if (this.form.password) payload.password = this.form.password

      try {
        await api.put(
          `/admin/users/update/${id}`,
          payload,
          { headers: this.authHeaders() }
        )
        this.poruka = "Korisnik azuriran!"
        this.cancelEdit()
        await this.loadUsers()
      } catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da azuriram korisnika"
      }
    },

    async dodajKorisnika() {
      this.$router.push('/admin/users/add')
    },

    async obrisiKorisnika(id) {
      this.poruka = ""
      this.greska = ""
      if (!confirm("Obrisati korisnika?")) return

      try {
        await api.delete(`/admin/users/delete/${id}`, {
          headers: this.authHeaders()
        })
        this.poruka = "Korisnik obrisan!"
        await this.loadUsers()
      } catch (e) {
        this.greska = e?.response?.data?.error || e?.response?.data?.message || "Ne mogu da obrisem korisnika"
      }
    }
  },
  mounted() {
    this.loadUsers()
  }
}
</script>

<template>
  <div class="container mt-4">
    <h3>Admin: Korisnici</h3>

    <p class="text-success" v-if="poruka">{{ poruka }}</p>
    <p class="text-danger" v-if="greska">{{ greska }}</p>

    <div class="d-flex justify-content-end mb-3">
      <button class="btn btn-success" @click="dodajKorisnika">
        + Dodaj korisnika
      </button>
    </div>

    <table class="table table-striped align-middle">
      <thead>
      <tr>
        <th>ID</th>
        <th>Username</th>
        <th>Email</th>
        <th>Godina rodjenja</th>
        <th>Profilna slika</th>
        <th>Role</th>
        <th>Novac</th>
        <th>New password</th>
        <th></th>
      </tr>
      </thead>

      <tbody>
      <tr v-for="u in users" :key="u.id">
        <td>{{ u.id }}</td>

        <td v-if="idZaIzmenu !== u.id">{{ u.username }}</td>
        <td v-else><input class="form-control" v-model="form.username" /></td>

        <td v-if="idZaIzmenu !== u.id">{{ u.email }}</td>
        <td v-else><input class="form-control" v-model="form.email" /></td>

        <td v-if="idZaIzmenu !== u.id">{{ u.godina_rodjenja }}</td>
        <td v-else><input class="form-control" type="number" v-model="form.godina_rodjenja" /></td>

        <td v-if="idZaIzmenu !== u.id">{{ u.profilna_slika }}</td>
        <td v-else><input class="form-control" v-model="form.profilna_slika" /></td>

        <td v-if="idZaIzmenu !== u.id">{{ u.role }}</td>
        <td v-else>
          <select class="form-select" v-model="form.role">
            <option value="kupac">kupac</option>
            <option value="prodavac">prodavac</option>
            <option value="administrator">administrator</option>
          </select>
        </td>

        <td v-if="idZaIzmenu !== u.id">{{ u.money }}</td>
        <td v-else><input class="form-control" type="number" v-model="form.money" /></td>

        <td v-if="idZaIzmenu !== u.id">-</td>
        <td v-else>
          <input class="form-control mb-1" type="password" placeholder="password" v-model="form.password" />
          <input class="form-control" type="password" placeholder="confirm" v-model="form.password2" />
        </td>

        <td class="text-end">
          <button v-if="idZaIzmenu !== u.id" class="btn btn-sm btn-primary me-2" @click="startEdit(u)">Edit</button>
          <button v-else class="btn btn-sm btn-success me-2" @click="sacuvajIzmene(u.id)">Save</button>
          <button v-if="idZaIzmenu === u.id" class="btn btn-sm btn-secondary me-2" @click="cancelEdit">Cancel</button>
          <button class="btn btn-sm btn-danger" @click="obrisiKorisnika(u.id)">Delete</button>
        </td>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
</style>
