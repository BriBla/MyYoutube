<template>
  <body>
    <h1> Videos </h1> <br>
    <div v-for="video in videos" :key="video.id">
        <h4> {{ video.name }} </h4>
        <p>
            Durée : {{ video.duration }} <br>
            Date de création : {{ video.created_at }} <br>
            Créateur : {{ video.user.pseudo }} <br>
            Disponibilité : {{ video.enabled }}
        </p> <br>
    </div>
  </body>
</template>

<script>
import axios from "axios"
axios.defaults.baseURL = "http://127.0.0.1:5000"

export default {
  data() {
    return {
      videos: [],
    };
  },
  mounted() {
      axios({
          url: "/videos",
          method: "get",
      })
      .then((response) => {
          console.log(response.data.data[0].id)
          this.videos = response.data.data
      })
      .catch((response) => {
          response.log(response)
      })
  },
  methods: {
    details() {
     videoId = this.video.id
      axios({
          method: 'get',
          url: '/video/' + videoId
      })
    },
    LogOut() {
      this.flashMessage.show({status: 'warning', title: 'User', message: 'Log OUT !'});
      document.cookie = "token=;expires=Thu, 01 Jan 1970 00:00:00 GMT"
      document.cookie = "id=;expires=Thu, 01 Jan 1970 00:00:00 GMT"
      window.location.assign('/login');
    },
  }
};
</script>