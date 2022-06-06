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
      </nav>
    </div>
  <div class="container-fluid" style="margin-top:100px">
    <div class="" style="margin-top:100px">
      <div class="rounded d-flex justify-content-center">
        <div class="col-md-4 col-sm-12 shadow-lg p-5 bg-light">
          <div class="text-center">
            <h3 class="text-danger">Upload video</h3>
          </div>
          <div class="p-4">
            <form action="">
              <div class="input-group mb-3">
                <div class="input-group-prepend">
                  <span class="input-group-text bg-danger"><i class="bi bi-play-btn-fill text-white"></i></span>
                </div>
                <input type="text" class="form-control" placeholder="Title" v-model="video.title" required>
              </div>
              <div>
                <input
                  type="file"
                  @change="uploadFile"
                  ref="file"
                />
              </div>
              <div class="d-grid mt-4 col-6 mx-auto">
                  <button class="btn btn-danger" type="button"   v-on:click='upload()'><i class="bi bi-play-btn-fill"></i>&nbsp;Upload</button>
              </div>
                <p class="text-center mt-3">Don't have an account ?
                    <span class="text-danger" onclick="window.location.href='/register';" style="cursor:alias">&nbsp;<i class="bi bi-play-btn-fill"></i>&nbsp;Register</span>
                </p>
            </form>
          </div>
        </div>
      </div>
    </div>
      <FlashMessage></FlashMessage>
  </div>
  <footer>
    <div class="d-flex justify-content-around mt-2">
      <p>
        The site <i class="bi bi-play-btn-fill"></i>&nbsp;myYoutube is
        copyright&copy; team <a href="#" v-b-popover.hover.top="'Monke, Demisfowl, Vorgans'" title="Team VBC">VBC</a>
      </p>
    </div>
  </footer>
</body>
</template>

<script>
import axios from "axios"
import Vue from 'vue';
import FlashMessage from '@smartweb/vue-flash-message';
Vue.use(FlashMessage);
let cookies = document.cookie
let cookiesSplited = cookies.split(';')
let userToken = cookiesSplited[1].split('=')
let userId = cookiesSplited[0].split('=')

export default {
  data() {
    return {
      video: {
          title: '',
          file: '',
      },
    };
  },
  methods: {
    uploadFile(){
        this.Videos = this.$refs.file.files[0]

    },
    upload(){
        const FromData = require('form-data')
        var formData = new FormData()

        formData.append('name', this.video.title)
        formData.append('source', this.Videos)
        axios({
            method: "post",
            url: "http://127.0.0.1:5000/user/" + userId[1] + "/video",
            data: formData,
            headers: {
                "Content-Type": "multipart/form-data",
                "Authorization": "Bearer " + userToken[1]
            },
        })
        .then((response) => {
            const FromData = require('form-data')
            var formData2 = new FormData()
            formData2.append('mail', response.data.mail)

            console.log(response)
            axios({
                method: 'patch',
                url: 'http://127.0.0.1:5000/video/' + response.data.video.id,
                headers: {
                  "Content-Type": "multipart/form-data",
                  "Authorization": "Bearer " + userToken[1]
                },
            })
            .then((response) => {
              this.flashMessage.show({status: 'success', title: 'Succes', message: 'Video Upload !'});
              console.log(response)
              window.location.assign('/');
            })
            .catch((response) => {
              console.log(response)
              this.flashMessage.show({status: 'error', title: 'Error', message: 'Bad Request !'});
            })
        })
        .catch((response) => {
            console.log(response)
        })
    },
    LogOut() {
      this.flashMessage.show({status: 'warning', title: 'User', message: 'Log OUT !'});
      document.cookie = "token=;expires=Thu, 01 Jan 1970 00:00:00 GMT"
      document.cookie = "id=;expires=Thu, 01 Jan 1970 00:00:00 GMT"
      window.location.assign('/login');
    },
  },
};
</script>