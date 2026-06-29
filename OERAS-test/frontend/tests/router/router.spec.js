import router from '@/router/index.js';

describe('前端路由配置测试', () => {
  test('包含登录、注册、考试、答题、准考证等核心路由', () => {
    const paths = router.options.routes.map(route => route.path);
    expect(paths).toContain('/');
    expect(paths).toContain('/answer');
    expect(paths).toContain('/login');
    expect(paths).toContain('/register');
    expect(paths).toContain('*');

    const root = router.options.routes.find(route => route.path === '/');
    const childPaths = root.children.map(route => route.path);
    expect(childPaths).toEqual(expect.arrayContaining([
      'exam', 'practice', 'grade', 'center', 'password', 'paper', 'score', 'admit-card'
    ]));
  });
});
