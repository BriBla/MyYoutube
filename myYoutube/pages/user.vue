<template>
  <body>
    <div class="fixed-top">
      <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <a class="navbar-brand" href="#">
          <button
            class="btn btn-danger dropdown-toggle"
            type="button"
            id="dropdownMenuButton"
            data-toggle="dropdown"
            aria-haspopup="true"
            aria-expanded="false"
          >
            <i class="bi bi-play-btn-fill"></i>&nbsp;myYoutube
          </button>
          <div class="dropdown-menu" aria-labelledby="dropdownMenuButton">
            <a class="dropdown-item" href="#">Action</a>
            <a class="dropdown-item" href="#">Another action</a>
            <a class="dropdown-item" href="#">Something else here</a>
          </div></a
        >

        <div class="collapse navbar-collapse" id="navbarSupportedContent">
          <ul class="navbar-nav mr-auto">
            <li class="nav-item">
              <a class="nav-link" href="/">Home</a>
            </li>
            <li class="nav-item active">
              <a class="nav-link" href="/user">User</a>
            </li>
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
        <table class="table">
          <thead class="thead-dark">
            <tr>
              <th scope="col">#</th>
              <th scope="col">Pseudo</th>
              <th scope="col">Username</th>
              <th scope="col">Created At</th>
              <th scope="col"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredUsers" :key="user.id">
              <th scope="row">{{ user.id }}</th>
              <td>{{ user.pseudo }}</td>
              <td>{{ user.username }}</td>
              <td>{{ user.created_at }}</td>
              <td>
                <div class="btn-group">
                  <button type="button" class="btn btn-sm btn-outline-warning">
                    Edit
                  </button>
                  <button type="button" class="btn btn-sm btn-outline-danger">
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </body>
</template>

<script>
import axios from "axios";
export default {
  data() {
    return {
      users: [],
      search: "",
    };
  },
  mounted() {
    try {
      axios
        .get("http://127.0.0.1:5000/users")
        .then((response) => (console.log(response),this.users = response.data.data));
    } catch (e) {
      console.error(e);
    }
  },
  computed: {
    filteredUsers: function () {
      if (!this.search) {
        return this.users;
      }
      return this.users.filter((user) => {
        return (user =
          user.pseudo.toLowerCase().includes(this.search.toLowerCase()) ||
          user.username.toLowerCase().includes(this.search.toLowerCase()) ||
          user.created_at.toLowerCase().includes(this.search.toLowerCase()));
      });
    },
  },
};
</script>