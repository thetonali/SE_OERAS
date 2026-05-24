import { shallowMount } from '@vue/test-utils';
import Center from './Center';

describe('<Center/>', () => {
	const wrapper = shallowMount(Center);

	// 快照测试
	it('snapshot测试', () => {
		const wrapper2 = shallowMount(Center);
		expect(wrapper2.html()).toMatchSnapshot()
		wrapper2.destroy()
    })
  });