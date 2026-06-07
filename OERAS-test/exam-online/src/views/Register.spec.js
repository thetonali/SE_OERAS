import { shallowMount } from '@vue/test-utils';
import Register from './Register';

describe('<Register/>', () => {
	const wrapper = shallowMount(Register);

	// 快照测试
	it('snapshot测试', () => {
		const wrapper2 = shallowMount(Register);
		expect(wrapper2.html()).toMatchSnapshot()
		wrapper2.destroy()
    })
  });