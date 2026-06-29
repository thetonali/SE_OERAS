import { shallowMount } from '@vue/test-utils';
import Login from '@/views/Login.vue';

const flushPromises = () => new Promise(resolve => setTimeout(resolve, 0));

const mountLogin = () => shallowMount(Login, {
  stubs: ['el-form', 'el-form-item', 'el-input', 'el-button', 'el-alert'],
  mocks: {
    $router: { push: jest.fn() },
    $message: { success: jest.fn(), error: jest.fn() },
    $store: { commit: jest.fn() }
  }
});

describe('登录页面功能测试', () => {
  beforeEach(() => {
    sessionStorage.clear();
    localStorage.clear();
    global.axios = window.axios = {
      post: jest.fn(() => Promise.resolve({
        status: 200,
        data: {
          token: 'token-001',
          user: { id: 1, username: 'student001' },
          student: { id: 1, name: 'Student001', avatar: '/avatar.png' }
        }
      }))
    };
  });

  test('登录成功后写入全局状态并进入考试中心', async () => {
    const wrapper = mountLogin();
    wrapper.vm.$refs.loginFormRef = {
      validate: callback => callback(true)
    };
    await wrapper.setData({
      loginForm: {
        username: 'student001',
        password: 'pass123456'
      }
    });

    wrapper.vm.handleLogin();
    await flushPromises();

    expect(global.axios.post).toHaveBeenCalledWith('api/jwt-auth/', {
      username: 'student001',
      password: 'pass123456'
    });
    expect(wrapper.vm.$store.commit).toHaveBeenCalledWith('setUser', {
      id: 1,
      username: 'student001'
    });
    expect(wrapper.vm.$store.commit).toHaveBeenCalledWith('setStudent', {
      id: 1,
      name: 'Student001',
      avatar: '/avatar.png'
    });
    expect(wrapper.vm.$store.commit).toHaveBeenCalledWith('setAuthorization', 'token-001');
    expect(localStorage.getItem('studentAvatar')).toBe('/avatar.png');
    expect(wrapper.vm.$router.push).toHaveBeenCalledWith('/exam');
  });

  test('表单校验失败时不发送登录请求', () => {
    const wrapper = mountLogin();
    wrapper.vm.$refs.loginFormRef = {
      validate: callback => callback(false)
    };

    wrapper.vm.handleLogin();

    expect(global.axios.post).not.toHaveBeenCalled();
  });
});
