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
                    </b-dropdown>
                </div></a>
            </nav>
        </div>
        <div class="container-fluid" style="margin-top:100px">
            <div class="" style="margin-top:100px">
                <div class="rounded d-flex justify-content-center">
                    <div class="col-md-4 col-sm-12 shadow-lg p-5 bg-light">
                        <div class="text-center">
                            <h3 class="text-danger">Create Account</h3>
                        </div>
                        <div class="p-4">
                            <form action="">
                                <div class="input-group mb-3">
                                    <div class="input-group-prepend">
                                        <span class="input-group-text bg-danger"><i
                                            class="bi bi-person-plus-fill text-white"></i></span>
                                    </div>
                                    <input type="text" class="form-control" placeholder="Username" v-model="form.username" required>
                                </div>
                                <div class="input-group mb-3">
                                    <div class="input-group-prepend">
                                        <span class="input-group-text bg-danger"><i
                                            class="bi bi-person-circle text-white"></i></span>
                                    </div>
                                    <input type="text" class="form-control" placeholder="Pseudo" v-model="form.pseudo" required>
                                </div>
                                <div class="input-group mb-3">
                                    <div class="input-group-prepend">
                                    <span class="input-group-text bg-danger"><i
                                            class="bi bi-envelope text-white"></i></span>
                                    </div>
                                    <input type="email" class="form-control" placeholder="Email" v-model="form.email" required>
                                </div>
                                <div class="input-group mb-3">
                                    <div class="input-group-prepend">
                                    <span class="input-group-text bg-danger"><i
                                            class="bi bi-key-fill text-white"></i></span>
                                    </div>
                                    <input type="password" class="form-control" placeholder="password" v-model="form.password" required>
                                </div>
                                <div class="d-grid mt-4 col-6 mx-auto">
                                    <button class="btn btn-danger" type="button" v-on:click='register()'><i class="bi bi-play-btn-fill"></i>&nbsp;Register</button>
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
axios.defaults.baseURL = "http://127.0.0.1:5000"

export default{
    data() {
      return {
        form: {
            username: '',
            pseudo: '',
            email: '',
            password: ''
        },
      }
    },
    methods:{
        register(){
            const FormData = require('form-data')
            var formData = new FormData()
            formData.append('username', this.form.username)
            formData.append('pseudo', this.form.pseudo)
            formData.append('email', this.form.email)
            formData.append('password', this.form.password)

            axios({
                method: "post",
                url: "/user",
                data: formData,
                headers: { "Content-Type": "multipart/form-data" },
                })
                .then((response) => {
                    this.flashMessage.show({status: 'success', title: 'Succes', message: 'Submit register !'});
                    console.log(response)
                    window.location.assign('/login');
                })
                .catch((response) => {
                    this.flashMessage.show({status: 'error', title: 'Error', message: 'Bad Request!'});
                    console.log(response)
                });
        }
    }

}

</script>