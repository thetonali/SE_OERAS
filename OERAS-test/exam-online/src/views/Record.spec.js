import { shallowMount } from '@vue/test-utils';
import Record from './Record';

describe('<Record/>', () => {
	const wrapper = shallowMount(Record);

	// 快照测试
	it('snapshot测试', () => {
		const wrapper2 = shallowMount(Record);
		expect(wrapper2.html()).toMatchSnapshot()
		wrapper2.destroy()
    })
  });