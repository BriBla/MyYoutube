<template>
  <div>
    <h1>Test</h1>
    <div>
      {{ phrase.message }} <br> 
      {{ phrase.tes_points }} <br>
      {{ phrase.temps_perdu }}
    </div>
    <h2>Users : </h2>
    <div v-for="user in users" :key="user.id">
      <h5> User {{ user.id }} : </h5>
      <pre>   Pseudo : {{ user.pseudo }} </pre>
      <pre>   Username : {{ user.username }} </pre>
      <pre>   Creation date : {{ user.created_at }} </pre>
    </div>
  </div>
</template>

<script>
import axios from "axios"
axios.defaults.baseURL = "http://127.0.0.1:5000"

export default{
    data() {
      return {
        phrase: {
          "message": "Default",
          'tes_points': 4,
          "temps_perdu": "aucun"
        },
        users : []
      }
    },
    mounted(){
      axios
          .get('/hello')
          .then(response => this.phrase = response.data),
      axios
        .get('/users')
        .then(response => this.users = response.data.data)
    }
}

</script>
