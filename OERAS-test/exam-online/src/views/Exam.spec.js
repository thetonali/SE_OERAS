import { shallowMount } from '@vue/test-utils';
import Exam from './Exam';

describe('<Exam/>', () => {
	const wrapper = shallowMount(Exam);

	// 快照测试
	it('snapshot测试', () => {
		const wrapper2 = shallowMount(Exam);
		expect(wrapper2.html()).toMatchSnapshot()
		wrapper2.destroy()
    })
  });