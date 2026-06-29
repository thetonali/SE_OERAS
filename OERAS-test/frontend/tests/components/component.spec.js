import { shallowMount } from '@vue/test-utils';
import Pagination from '@/components/Pagination.vue';
import TimeCountDown from '@/components/TimeCountDown.vue';
import SlideVerification from '@/components/SlideVerification.vue';

const factory = (component, options = {}) => shallowMount(component, {
  stubs: ['el-pagination', 'el-button', 'el-input', 'el-form', 'el-form-item'],
  ...options
});

describe('公共组件单元测试', () => {
  test('Pagination 渲染分页控件并触发分页事件', () => {
    const wrapper = factory(Pagination, {
      propsData: { count: 42 }
    });
    expect(wrapper.exists()).toBe(true);
    wrapper.vm.handleSizeChange(10);
    wrapper.vm.handleCurrentChange(2);
    expect(wrapper.emitted('size-change')[0]).toEqual([10]);
    expect(wrapper.emitted('current-change')[0]).toEqual([2]);
    expect(wrapper.html()).toMatchSnapshot();
  });

  test('TimeCountDown 根据分钟数渲染倒计时并在归零时触发交卷事件', () => {
    const wrapper = factory(TimeCountDown, {
      propsData: { totalTime: 1 }
    });
    expect(wrapper.vm.timeLeft).toBe(60);
    wrapper.setData({ timeLeft: 0 });
    expect(wrapper.vm.showTimeLeft).toBeTruthy();
    expect(wrapper.emitted('hand-in')).toBeTruthy();
    expect(wrapper.html()).toMatchSnapshot();
  });

  test('SlideVerification 初始渲染稳定', () => {
    const wrapper = factory(SlideVerification);
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.html()).toMatchSnapshot();
  });
});
