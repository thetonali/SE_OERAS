import { shallowMount } from '@vue/test-utils';
import Answer from './Answer';


describe('<Answer/>', () => {
	const wrapper = shallowMount(Answer);

	// 快照测试
	it('snapshot测试', async () => { 
		const wrapper2 = shallowMount(Answer);
		const result = await wrapper2.html()
		expect(result).toMatchSnapshot()
		wrapper2.destroy()
    })

	
  });
