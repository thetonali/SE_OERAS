import { shallowMount } from '@vue/test-utils';
import Mistakes from './Mistakes';

describe('<Mistakes/>', () => {
	const wrapper = shallowMount(Mistakes);

	// 快照测试
	it('snapshot测试', () => {
		const wrapper2 = shallowMount(Mistakes);
		expect(wrapper2.html()).toMatchSnapshot()
		wrapper2.destroy()
    })
  });
