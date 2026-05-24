import { shallowMount } from '@vue/test-utils';
import Practice from './Practice';

describe('<Practice/>', () => {
	const wrapper = shallowMount(Practice);

	// 快照测试
	it('snapshot测试', () => {
		const wrapper2 = shallowMount(Practice);
		expect(wrapper2.html()).toMatchSnapshot()
		wrapper2.destroy()
    })
  });