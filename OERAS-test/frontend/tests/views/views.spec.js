import { shallowMount, createLocalVue } from '@vue/test-utils';
import VueRouter from 'vue-router';
import Login from '@/views/Login.vue';
import Register from '@/views/Register.vue';
import Exam from '@/views/Exam.vue';
import Practice from '@/views/Practice.vue';
import Grade from '@/views/Grade.vue';
import Center from '@/views/Center.vue';
import Password from '@/views/Password.vue';
import Record from '@/views/Record.vue';
import AdmitCard from '@/views/AdmitCard.vue';
import Answer from '@/views/Answer.vue';
import Paper from '@/views/Paper.vue';
import Score from '@/views/Score.vue';
import Error from '@/views/Error.vue';

const localVue = createLocalVue();
localVue.use(VueRouter);

const stubs = [
  'router-link', 'router-view', 'el-container', 'el-main', 'el-header', 'el-aside',
  'el-menu', 'el-menu-item', 'el-form', 'el-form-item', 'el-input', 'el-button',
  'el-card', 'el-table', 'el-table-column', 'el-pagination', 'el-select', 'el-option',
  'el-radio', 'el-radio-group', 'el-checkbox', 'el-dialog', 'el-tag', 'el-row', 'el-col',
  'el-alert', 'el-date-picker', 'el-time-picker'
];

const mountView = component => shallowMount(component, {
  localVue,
  router: new VueRouter(),
  stubs,
  mocks: {
    $axios: {
      get: jest.fn(() => Promise.resolve({ data: { results: [] } })),
      post: jest.fn(() => Promise.resolve({ data: {} })),
      patch: jest.fn(() => Promise.resolve({ data: {} }))
    },
    $message: { success: jest.fn(), error: jest.fn(), warning: jest.fn() },
    $confirm: jest.fn(() => Promise.resolve())
  }
});

const cases = [
  ['Login', Login],
  ['Register', Register],
  ['Exam', Exam],
  ['Practice', Practice],
  ['Grade', Grade],
  ['Center', Center],
  ['Password', Password],
  ['Record', Record],
  ['AdmitCard', AdmitCard],
  ['Answer', Answer],
  ['Paper', Paper],
  ['Score', Score],
  ['Error', Error]
];

describe('前端视图快照测试', () => {
  test.each(cases)('%s 页面初始渲染稳定', async (name, component) => {
    const wrapper = mountView(component);
    await wrapper.vm.$nextTick();
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.html()).toMatchSnapshot();
  });
});
