import Vue from 'vue';

Vue.config.productionTip = false;
Vue.config.devtools = false;

const storageFactory = () => {
  let store = {};
  return {
    getItem: key => store[key] || null,
    setItem: (key, value) => { store[key] = String(value); },
    removeItem: key => { delete store[key]; },
    clear: () => { store = {}; }
  };
};

Object.defineProperty(window, 'localStorage', { value: storageFactory() });
Object.defineProperty(window, 'sessionStorage', { value: storageFactory() });

if (!window.axios) {
  window.axios = {
    get: jest.fn(() => Promise.resolve({ data: {} })),
    post: jest.fn(() => Promise.resolve({ data: {} })),
    patch: jest.fn(() => Promise.resolve({ data: {} }))
  };
}
