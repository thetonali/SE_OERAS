# OERAS Test Suite

本目录是第五次作业的软件测试交付目录，只保存测试工程、运行脚本、测试记录和报告模板，不再重复保存前端/后端源代码。

## 已清理内容

以下内容已经从 `OERAS-test` 中删除：

- 重复前端源码副本：`OERAS-test/exam-online/`
- 重复后端源码副本：`OERAS-test/ExamOnline/`
- 前端依赖目录：`node_modules/`
- 旧覆盖率输出：`coverage/`
- 与测试无直接关系的部署配置副本

真实源码仍保留在上级目录：

- 前端源码：`../exam-online/`
- 后端源码：`../ExamOnline/`

## 当前目录结构

```text
OERAS-test
├─ frontend
│  ├─ tests/components       # 前端组件单元测试
│  ├─ tests/views            # 前端页面快照与交互测试
│  ├─ tests/router           # 路由与导航守卫测试
│  ├─ tests/setup            # Jest mock 与测试环境初始化
│  ├─ jest.config.js
│  └─ package.json
├─ backend
│  ├─ README.md
│  └─ run_backend_tests.ps1
├─ reports
│  ├─ bug-list.md
│  ├─ manual-test-record.md
│  └─ README.md
├─ run_all_tests.ps1
└─ README.md
```

## 前端测试执行

```powershell
cd OERAS-test\frontend
npm install
npm run test:coverage
```

测试代码通过 `jest.config.js` 的 `@/` 映射直接引用 `../../exam-online/src`，避免测试副本与真实源码不一致。

## 后端测试执行

```powershell
cd OERAS-test\backend
.\run_backend_tests.ps1
```

后端测试仍使用真实后端源码中各 app 的 `tests/` 目录：`user/tests`、`exam/tests`、`question/tests`、`record/tests`。

## 一键执行

```powershell
cd OERAS-test
.\run_all_tests.ps1
```

如果本机未安装依赖，先分别执行前端 `npm install` 和后端 `pip install -r ..\ExamOnline\requirements.txt`。
