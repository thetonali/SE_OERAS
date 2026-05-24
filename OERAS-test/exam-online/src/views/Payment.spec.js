import { shallowMount } from '@vue/test-utils';
import Payment from './Payment';

describe('<Payment/>', () => {
	const wrapper = shallowMount(Payment);

	// 快照测试
	it('snapshot测试', () => {
		const wrapper2 = shallowMount(Payment);
		expect(wrapper2.html()).toMatchSnapshot()
		wrapper2.destroy()
    })
  });