"use strict";

import Vue from 'vue';
import axios from "axios";

let config = {
  // baseURL: process.env.baseURL || process.env.apiUrl || ""
  // timeout: 60 * 1000, // Timeout
  //baseURL: "http://127.0.0.1:8000",
  // withCredentials: true, // Check cross-site Access-Control
};

const _axios = axios.create(config);

// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

_axios.interceptors.request.use(
  function(config) {
    // Do something before request is sent
    // Add token to headers
    // let token = localStorage.getItem('Authorization');
    // if (token) {
    //   // 检查 token 是否已经包含了 'JWT ' 前缀
    //   // 如果没有包含，则手动帮它加上，以符合 Django 后端的严格要求
    //   if (!token.startsWith('JWT ')) {
    //       token = 'JWT ' + token;
    //   }
    //   config.headers.Authorization = token;
    // }
    if (localStorage.getItem('Authorization')) {
      config.headers.Authorization = localStorage.getItem('Authorization');
    }
    // Add CSRF token to headers
    config.headers['X-CSRFToken'] = getCookie('csrftoken');
    return config;
  },
  function(error) {
    // Do something with request error
    return Promise.reject(error);
  }
);

// Add a response interceptor
_axios.interceptors.response.use(
  function(response) {
    // Do something with response data
    return response;
  },
  function(error) {
    // Do something with response error
    return Promise.reject(error);
  }
);

Plugin.install = function(Vue, options) {
  Vue.axios = _axios;
  window.axios = _axios;
  Object.defineProperties(Vue.prototype, {
    axios: {
      get() {
        return _axios;
      }
    },
    $axios: {
      get() {
        return _axios;
      }
    },
  });
};

Vue.use(Plugin)

export default Plugin;
