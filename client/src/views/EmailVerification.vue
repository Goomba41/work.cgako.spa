<template>
  <div class="about">
    <b-button variant="info" @click="sendVerify">Верифицировать</b-button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'About',
  props: ['token'],
  methods: {
    sendVerify(){
      return axios.put('/API/v1.0.0/emails/verification/'+ this.token +'?dbg=true')
        .then((response) => {
          // eslint-disable-next-line
          console.log(response);
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  }
}
</script>
