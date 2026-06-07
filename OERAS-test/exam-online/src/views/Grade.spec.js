import { shallowMount } from '@vue/test-utils';
import Grade from './Grade';

describe('<Grade/>', () => {
	const wrapper = shallowMount(Grade);

	// 快照测试
	it('snapshot测试', () => {
		const wrapper2 = shallowMount(Grade);
		expect(wrapper2.html()).toMatchSnapshot()
		wrapper2.destroy()
    })
  });
