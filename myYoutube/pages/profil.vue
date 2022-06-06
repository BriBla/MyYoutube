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
                            <h3 class="text-danger">Profil</h3>
                        </div>
                        <div class="p-4">
                            <form action="">
                                <div class="input-group mb-3">
                                    <div class="input-group-prepend">
                                        <span class="input-group-text bg-danger"><i
                                            class="bi bi-person-plus-fill text-white"></i></span>
                                    </div>
                                    <input type="text" class="form-control" v-model="form.username" required>
                                </div>
                                <div class="input-group mb-3">
                                    <div class="input-group-prepend">
                                        <span class="input-group-text bg-danger"><i
                                            class="bi bi-person-circle text-white"></i></span>
                                    </div>
                                    <input type="text" class="form-control" v-model="form.pseudo" required>
                                </div>
                                <div class="input-group mb-3">
                                    <div class="input-group-prepend">
                                    <span class="input-group-text bg-danger"><i
                                            class="bi bi-envelope text-white"></i></span>
                                    </div>
                                    <input type="email" class="form-control" v-model="form.email" required>
                                </div>
                                <div class="input-group mb-3">
                                    <div class="input-group-prepend">
                                    <span class="input-group-text bg-danger"><i
                                            class="bi bi-key text-white"></i></span>
                                    </div>
                                    <input type="password" class="form-control" v-model="form.password" required>
                                </div>
                                <div class="d-grid mt-4 col-6 mx-auto">
                                    <button class="btn btn-danger" type="button" v-on:click='update()'><i class="bi bi-play-btn-fill"></i>&nbsp;Update</button>
                                </div>
                                <p class="text-center mt-3">Already have an account?
                                    <span class="text-danger" onclick="window.location.href='/login';" style="cursor:alias">&nbsp;<i class="bi bi-play-btn-fill"></i>&nbsp;Sign in</span>
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
axios.defaults.baseURL = ""

let cookies = document.cookie
let cookiesSplited = cookies.split(';')
let userToken = cookiesSplited[1].split('=')
let userId = cookiesSplited[0].split('=')

export default{
    data() {
      return {
        user: {
            id: userId[1],
            token: userToken[1],
            email: '',
            pseudo: '',
            username: '',
        },
        form: {
            email: '',
            username: '',
            pseudo: '',
            password: ''
        }
      }
    },
    mounted () {
        axios ({
            method: "get",
            url: "http://127.0.0.1:5000/user/" + userId[1],
            headers: {
                "Authorization": "Bearer " + userToken[1]
            }
        })
        .then((response) => {
            console.log(response)
            this.user.email = response.data.user.email
            this.user.pseudo = response.data.user.pseudo
            this.user.username = response.data.user.username
            this.form.email = this.user.email
            this.form.pseudo = this.user.pseudo
            this.form.username = this.user.username
        })
        .catch((response) => {
            console.log(response)
        })

    },
    methods:{
        LogOut() {
            document.cookie = "token=;expires=Thu, 01 Jan 1970 00:00:00 GMT"
            document.cookie = "id=;expires=Thu, 01 Jan 1970 00:00:00 GMT"
            window.location.assign('/login')
        },

        update(){
            const FormData = require('form-data')
            var formData = new FormData()
            if(this.form.username != '') {
                formData.append('username', this.form.username)
            }
            if(this.form.pseudo != '') {
                formData.append('pseudo', this.form.pseudo)
            }
            if(this.form.pseudo != '') {
                formData.append('email', this.form.email)
            }
            if(this.form.password != '') {
                formData.append('password', this.form.password)
                const FormData = require('form-data')
                var formData2 = new FormData()
                formData2.append('email', this.form.email)
                formData2.append('email type', '1')
                axios({
                    method:"post",
                    url: "http://127.0.0.1:5002/mail",
                    data: formData2,
                    headers: {
                    "Content-Type": "multipart/form-data"
                    }
                }).then((response) => {
                    console.log(response)
                }).catch((response) => {
                    console.log(response)
                })
            }

            axios({
                method: "put",
                url: "http://127.0.0.1:5000/user/" + userId[1],
                data: formData,
                headers: {
                    "Content-Type": "multipart/form-data",
                    "Authorization": "Bearer " + userToken[1]
                }
            })
            .then((response) => {
                this.flashMessage.show({status: 'success', title: 'Succes', message: 'Profil Update !'});
                console.log(response)
                window.location.reload();
            })
            .catch((response) => {
                console.log(response)
                this.flashMessage.show({status: 'error', title: 'Error', message: 'Bad Request !'});
            })
        }
    }

}
</script>