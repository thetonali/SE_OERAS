# 后端测试说明

后端测试代码保留在真实后端源码中，避免在测试目录复制一份后端工程造成代码不一致。

## 测试对象

- `../ExamOnline/user/tests/`：用户、班级、注册、登录、密码修改相关测试
- `../ExamOnline/exam/tests/`：试卷、考试、报名、成绩、主观题阅卷相关测试
- `../ExamOnline/question/tests/`：题库模型、题目抽取、组卷接口相关测试
- `../ExamOnline/record/tests/`：练习/答题记录相关测试

## 执行命令

```powershell
.\run_backend_tests.ps1
```

生成覆盖率报告：

```powershell
.\run_backend_tests.ps1 -Coverage
```

## 环境要求

后端运行前需要可用 Python 环境，并安装：

```powershell
pip install -r ..\..\ExamOnline\requirements.txt
```

如果使用项目原有 `venv`，需确保虚拟环境没有失效，且包含 `setuptools/pkg_resources`。
