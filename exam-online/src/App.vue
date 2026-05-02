<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
/* ===== 全局字体设置：宋体 ===== */
* {
  font-family: "SimSun", "宋体", "STSong", serif !important;
  box-sizing: border-box;
}

/* 覆盖 Element UI 的默认字体 */
.el-button,
.el-input,
.el-input__inner,
.el-form-item__label,
.el-table,
.el-menu,
.el-menu-item,
.el-submenu__title,
.el-dialog,
.el-message-box,
.el-select,
.el-option,
.el-tag,
.el-pagination,
.el-tabs,
.el-card,
.el-breadcrumb,
.el-dropdown-menu,
.el-tooltip,
.el-loading-text,
.el-empty__description {
  font-family: "SimSun", "宋体", "STSong", serif !important;
}

/* ===== 全局背景色：去掉贴图，改为纯色 ===== */
body {
  margin: 0;
  padding: 0;
  background-color: #f0f2f5;
  /* 移除任何背景图片 */
  background-image: none !important;
}

#app {
  height: 100vh;
  background-color: #f0f2f5;
  background-image: none !important;
}

/* ===== 去掉可能存在的全局背景图片 ===== */
html {
  background-image: none !important;
  background-color: #f0f2f5;
}
</style>