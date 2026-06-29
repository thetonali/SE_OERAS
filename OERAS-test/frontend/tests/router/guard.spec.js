import router from '@/router/index.js';

describe('前端路由守卫集成测试', () => {
  const runGuard = (toPath, token = null) => new Promise(resolve => {
    const guard = router.beforeHooks[0];
    if (token) {
      sessionStorage.setItem('Authorization', token);
    } else {
      sessionStorage.removeItem('Authorization');
    }
    guard({ path: toPath, meta: { title: 'Target Page' } }, { path: '/' }, resolve);
  });

  test('未登录访问业务页面时跳转登录页', async () => {
    const result = await runGuard('/exam');

    expect(result).toBe('/login');
    expect(document.title).toBe('Target Page');
  });

  test('登录页和注册页无需令牌即可访问', async () => {
    await expect(runGuard('/login')).resolves.toBeUndefined();
    await expect(runGuard('/register')).resolves.toBeUndefined();
  });

  test('已登录用户访问业务页面时放行', async () => {
    await expect(runGuard('/answer', 'Bearer test-token')).resolves.toBeUndefined();
  });
});
