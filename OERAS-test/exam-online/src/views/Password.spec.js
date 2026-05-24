import { shallowMount } from '@vue/test-utils';
import Password from './Password';

describe('<Password/>', () => {
	const wrapper = shallowMount(Password);

	// 快照测试
	it('snapshot测试', () => {
		const wrapper2 = shallowMount(Password);
		expect(wrapper2.html()).toMatchSnapshot()
		wrapper2.destroy()
    })
  });