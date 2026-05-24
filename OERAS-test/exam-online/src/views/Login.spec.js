import { shallowMount } from '@vue/test-utils';
import Login from './Login';

describe('<Login/>', () => {
	const wrapper = shallowMount(Login);

	// 快照测试
	it('snapshot测试', () => {
		const wrapper2 = shallowMount(Login);
		expect(wrapper2.html()).toMatchSnapshot()
		wrapper2.destroy()
    })
  });
