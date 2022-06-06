<template>
  <body>
    <div class="fixed-top">
      <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <a class="navbar-brand" href="#">
          <div>
          <b-dropdown id="dropdown-1" variant="danger" text="Danger" class="m-md-2">
                <template v-slot:button-content>
            <i class="bi bi-play-btn-fill"></i>&nbsp;myYoutube
            </template>
            <b-dropdown-item href="/">Home</b-dropdown-item>
            <b-dropdown-divider></b-dropdown-divider>
            <b-dropdown-item href="/login">Login</b-dropdown-item>
            <b-dropdown-item href="/profil">Profil</b-dropdown-item>
            <b-dropdown-item href="/upload">Upload</b-dropdown-item>
            <b-dropdown-item href="/register">Register</b-dropdown-item>
            <b-dropdown-divider></b-dropdown-divider>
            <b-dropdown-item @click="LogOut()">Log Out</b-dropdown-item>
          </b-dropdown>
      </div></a>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
          <ul class="navbar-nav mr-auto">
          </ul>
          <div class="form-inline my-2 my-lg-0">
            <input
              class="form-control mr-sm-2"
              type="text"
              placeholder="Search"
              aria-label="Search"
              v-model="search"
            />
          </div>
        </div>
      </nav>
    </div>
    <div class="album py-5 bg-light">
      <div class="container py-5">
        <div class="row">
          <div v-for="video in filteredVideos" :key="video.id" class="col-md-4">
            <div class="card mb-4 box-shadow">
                <video controls>
                  <source type="video/mp4" src='<%= BASE_URL %>favicon.ico'>
                  
                </video>
              <div class="card-body">
                <h5 class="card-title">Title : {{ video.name }}</h5>
                <p class="card-text">
                Creation : {{ video.created_at }}
                </p>
                <h6 class="card-subtitle mb-2">User : {{ video.user.pseudo }}</h6>
                <div class="d-flex justify-content-between align-items-center">
                  <div class="btn-group">
                    <button v-on:click='Delete(video)' type="button" class="btn btn-sm btn-outline-danger">
                      Delete
                    </button>
                  </div>
                  <small class="text-muted">Time : {{ video.duration }} mins</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    <FlashMessage></FlashMessage>
    </div>
    <footer>
      <div class="container">
        <p class="float-right">
          <a href="#">Back to top</a>
        </p>
        <p>
          The site <i class="bi bi-play-btn-fill"></i>&nbsp;myYoutube is
          copyright&copy; team <a href="#" v-b-popover.hover.top="'Monke, Demisfowl, Vorgans'" title="Team VBC">VBC</a>
        </p>
      </div>
    </footer>
  </body>
</template>

<script>
import axios from "axios";
import Vue from 'vue';
import FlashMessage from '@smartweb/vue-flash-message';
Vue.use(FlashMessage);
axios.defaults.baseURL = "http://127.0.0.1:5000";

let cookies = document.cookie
let cookiesSplited = cookies.split(';')
let userToken = cookiesSplited[1].split('=')
let userId = cookiesSplited[0].split('=')

export default {
  data() {
    return {
      videos: [],
      search: "",
    };
  },
  mounted() {
      axios({
          url: "http://127.0.0.1:5000/videos",
          method: "get",
      })
      .then((response) => {
          console.log(response.data.data[0].id)
          this.videos = response.data.data
      })
      .catch((response) => {
        this.flashMessage.show({status: 'info', title: 'myYoutube Appologize', message: 'Please Upload some Video Before Try !'});
        response.log(response)
      })
  },
  computed: {
    filteredVideos: function () {
      if (!this.search) {
        return this.videos;
      }
      return this.videos.filter((video) => {
        return (video =
          video.name.toLowerCase().includes(this.search.toLowerCase()) ||
          video.user.username.toLowerCase().includes(this.search.toLowerCase()) ||
          video.user.pseudo.toLowerCase().includes(this.search.toLowerCase()) ||
          video.created_at.toLowerCase().includes(this.search.toLowerCase()));
      });
    },
  },
  methods:{
    LogOut() {
        this.flashMessage.show({status: 'warning', title: 'User', message: 'Log OUT !'});
        document.cookie = "token=;expires=Thu, 01 Jan 1970 00:00:00 GMT"
        document.cookie = "id=;expires=Thu, 01 Jan 1970 00:00:00 GMT"
        window.location.assign('/login');
    },
    Delete(video){
      if(video.user.id != userId[1]) {
        this.flashMessage.show({status: 'error', title: 'Error', message: 'Only creator can delete!'});
        return false;
      }
      axios({
          method: "delete",
          url: "/video/" + video.id,
          headers: {
          "Content-Type": "multipart/form-data",
          "Authorization": "Bearer " + userToken[1]
          },
      })
      .then((response) => {
          this.flashMessage.show({status: 'success', title: 'Succes', message: 'Delete !'});
          console.log(response)
          window.location.reload();
      })
      .catch((response) => {
          this.flashMessage.show({status: 'error', title: 'Error', message: 'No access !'});
          console.log(response)
      });
    },
  },
};
</script>