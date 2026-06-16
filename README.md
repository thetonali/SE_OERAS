# 在线考试报名与管理系统实现说明文档

[toc]

## 1 提交文件

本次作业提交时，将以下内容与源码一起打包：

```text
SE_OERAS
├─ ExamOnline                  # 后端源码、数据库、迁移脚本、依赖文件
├─ exam-online                 # 前端源码、配置文件、构建脚本
├─ OERAS-test                  # 单元测试、覆盖率材料和测试版本代码
└─ 系统实现说明文档.md         # 本文档
```

以下内容可重新生成且体积较大：

- `exam-online/node_modules`
- `exam-online/dist`
- `__pycache__`
- `.pytest_cache`
- 前端覆盖率临时输出目录

本次作业提交的是可直接运行的演示版本，故保留 `db.sqlite3` 和必要的静态资源，不需要重新通过 `python manage.py migrate` 创建数据库。
（假如只有源码，则根据本文档中的说明通过迁移脚本 `python manage.py migrate` 创建数据库。）

## 2 系统简介

### 2.1 系统定位

本系统为“在线考试报名与管理系统”，面向学校课程考试、资格认证考试、竞赛选拔等场景，提供从学生注册登录、考试报名、准考证生成、在线答题、成绩查询，到教师/管理员维护题库、配置考试、导出考生信息、主观题阅卷的完整流程支持。

系统采用前后端分离的 Web 架构：

- 前端项目：`exam-online`
- 后端项目：`ExamOnline`
- 测试与覆盖率相关目录：`OERAS-test`

前端负责页面展示、路由跳转、登录态维护和接口调用；后端负责数据模型、业务规则、REST API、认证鉴权、后台管理、数据库持久化和阅卷辅助逻辑。

### 2.2 主要功能

#### 2.2.1 用户与登录功能

系统支持学生用户注册、登录、退出、个人中心和密码修改。
前端通过登录接口获取认证信息，并在后续请求中携带 `Authorization` 请求头。
后端基于 Django 自带用户模型、学生资料模型和 JWT 认证机制完成身份识别。

涉及模块：

- 前端页面：`Login.vue`、`Register.vue`、`Center.vue`、`Password.vue`
- 后端应用：`user`
- 主要接口：`/jwt-auth/`、`/register/`、`/students/`、`/update-pwd/`

#### 2.2.2 考试中心与考试报名

学生登录后可以进入考试中心查看可参加考试。
后端根据学生所在班级、考试是否限制班级、考试开始时间和结束时间过滤可见考试。
考试开始前，学生可以报名并生成准考证号；考试开始后不允许继续报名。

涉及模块：

- 前端页面：`Exam.vue`、`AdmitCard.vue`
- 后端模型：`Exam`、`Paper`、`ExamRegistration`
- 主要接口：`/exams/`、`/registrations/`

核心规则：

- 考试未限制班级时，所有学生可见；
- 考试限制班级时，仅指定班级学生可见；
- 已结束考试不再展示给学生；
- 报名记录由 `exam_id + student_id` 唯一约束保证同一学生不能重复报名同一场考试；
- 准考证号由后端自动生成，格式类似 `OERAS-日期-考试编号-学生编号-随机码`。

#### 2.2.3 题库管理与自动组卷

系统支持选择题、填空题、判断题、主观题四类题目。
题目按科目和难度等级维护，试卷配置中记录科目、难度、各题型数量和总分。
后端提供统一组卷接口，根据试卷配置从题库中随机抽取匹配题目。

涉及模块：

- 前端页面：`Paper.vue`、`Answer.vue`
- 后端应用：`question`
- 后端模型：`Choice`、`Fill`、`Judge`、`Subjective`
- 主要接口：`/api/paper/generate/`、`/choices/`、`/fills/`、`/judges/`、`/subjective/`

核心规则：

- 题目均包含 `subject` 科目字段和 `level` 难度字段；
- 组卷时按试卷科目和难度过滤题库；
- 选择题、填空题、判断题默认每题 2 分；
- 主观题默认每题 8 分；
- 试卷保存时根据各题型数量自动计算总分。

#### 2.2.4 在线答题与成绩记录

学生进入答题页面后完成客观题和主观题作答。
客观题可以直接计算得分，主观题答案保存后等待教师阅卷。
系统记录考试成绩、练习记录和各题型答题记录，便于学生查询成绩和错题。

涉及模块：

- 前端页面：`Answer.vue`、`Score.vue`、`Grade.vue`、`Record.vue`
- 后端应用：`exam`、`record`
- 后端模型：`Grade`、`Practice`、`SubjectiveAnswer`、`ChoiceRecord`、`FillRecord`、`JudgeRecord`、`SubjectiveRecord`
- 主要接口：`/grades/`、`/practices/`、`/records/choices/`、`/records/fills/`、`/records/judges/`、`/records/subjective/`、`/upload-subjective/`

#### 2.2.5 主观题阅卷与 AI 辅助评分

系统提供主观题匿名阅卷页面。
教师登录后台后可以查看待阅卷任务，系统在阅卷页面隐藏学生姓名、准考证号等身份信息，仅展示匿名编号、题目、标准答案/评分标准和学生答案。
教师录入最终分数和评语后，系统记录分数变更历史。

后端还提供 AI 辅助评分接口，基于学生答案和参考答案生成建议分数区间及评分理由。
AI 建议只作为参考，最终分数仍由教师保存。

涉及模块：

- 后端模型：`SubjectiveAnswer`、`SubjectiveReviewHistory`
- 后端服务：`exam.services.suggest_subjective_score`
- 主要页面/接口：`/review/tasks/`、`/review/tasks/<id>/`、`/api/ai-score/`、`/api/review/tasks/<id>/ai-suggestion/`

#### 2.2.6 管理后台与数据导出

系统集成 xadmin 后台，管理员可维护用户、班级、题库、试卷、考试、成绩等基础数据。
后端还提供考生名单导出功能，可以将某场考试报名学生、准考证号、班级、考试时间、成绩状态等信息导出为 Excel 文件。

涉及模块：

- 后台入口：`/xadmin/`
- API 文档入口：`/docs/`
- 导出接口：`/exams/<id>/export-students/`
- 依赖库：`openpyxl`

### 2.3 技术路线

#### 2.3.1 前端技术路线

前端采用 Vue 2 技术栈，通过 Vue CLI 构建单页应用。

主要技术：

- `Vue 2.6.11`：构建组件化页面；
- `Vue Router 3.1.5`：管理登录、考试中心、答题页、成绩页等路由；
- `Vuex 3.1.2`：管理全局状态；
- `Element UI 2.4.5`：提供表单、按钮、布局、提示等 UI 组件；
- `Axios 0.18.0`：封装 HTTP 请求；
- `Sass`：编写页面样式；
- `Vue CLI 4.2.0`：本地开发、构建和打包。

前端目录结构说明：

```text
exam-online
├─ public              # 前端静态入口资源
├─ src
│  ├─ assets           # 图片等资源
│  ├─ components       # 通用组件，如分页、倒计时、滑块验证
│  ├─ layout           # 页面整体布局
│  ├─ plugins          # axios、Element UI 插件封装
│  ├─ router           # 前端路由与登录导航守卫
│  ├─ store            # Vuex 状态管理
│  └─ views            # 业务页面
├─ package.json        # 前端依赖与脚本
└─ vue.config.js       # Vue CLI 配置
```

#### 2.3.2 后端技术路线

后端采用 Django + Django REST Framework 技术栈。

主要技术：

- `Python 3.x`：后端开发语言；
- `Django 3.0.3`：Web 框架与 ORM；
- `Django REST Framework 3.11.0`：REST API 开发；
- `djangorestframework-jwt 1.11.0`：JWT 登录认证；
- `django-filter 2.2.0`：接口过滤；
- `xadmin2 2.0.3`：后台管理；
- `django-import-export 2.0.2`：后台数据导入导出能力；
- `openpyxl 3.0.3`：Excel 文件导出；
- `SQLite`：开发与课程作业环境下的默认数据库。

后端目录结构说明：

```text
ExamOnline
├─ ExamOnline          # Django 项目配置目录
│  ├─ settings.py      # 全局配置、数据库、应用注册、DRF/JWT 配置
│  ├─ urls.py          # 全局路由与 API 注册
│  ├─ asgi.py
│  └─ wsgi.py
├─ user                # 用户、学生、班级、教师相关模型与接口
├─ exam                # 考试、试卷、成绩、报名、主观题阅卷相关逻辑
├─ question            # 选择题、填空题、判断题、主观题题库与组卷接口
├─ record              # 练习/答题记录
├─ static              # 后台和 DRF 静态资源
├─ db.sqlite3          # SQLite 数据库文件
├─ manage.py           # Django 管理脚本
└─ requirements.txt    # 后端依赖
```

#### 2.3.3 前后端交互路线

前端通过 Axios 调用后端 REST API。
请求拦截器负责自动附加登录认证信息和 CSRF Token：

- 登录后保存认证信息；
- 普通业务接口通过 `Authorization` 请求头携带认证状态；
- 涉及写操作时附加 `X-CSRFToken`；
- 前端路由守卫检查登录状态，未登录用户跳转至 `/login`。

后端通过 DRF 的 `DefaultRouter` 注册资源接口，接口统一返回 JSON 数据。
部分特殊功能使用 `APIView` 或普通 Django 视图实现，例如组卷、上传主观题答案、AI 辅助评分、匿名阅卷页面和 Excel 导出。

### 2.4 开发环境配置

#### 2.4.1 基础环境

建议开发环境如下：

- 操作系统：Windows 10/11 或 Linux/macOS；
- Python：建议 3.10 或 3.11；
- Node.js：建议 14.x 或 16.x；
- 包管理工具：`pip`、`npm`；
- 数据库：SQLite，开发环境无需额外安装数据库服务；
- IDE：PyCharm、Visual Studio Code 或 WebStorm；
- 版本管理：Git。

首先——创建并激活虚拟环境：

```bash
conda create --name exam python=3.11
conda activate exam
```

#### 2.4.2 后端环境配置

进入后端目录：

```bash
cd ExamOnline
```

安装依赖：

```bash
pip install -r requirements.txt
```

执行数据库迁移：

```bash
python manage.py migrate
```

如需创建后台管理员账号：

```bash
python manage.py createsuperuser
```

启动后端服务：

```bash
python manage.py runserver
```

常用访问地址：

- 后端 API 根路径：`http://127.0.0.1:8000/`
- xadmin 后台：`http://127.0.0.1:8000/xadmin/` （即教师与管理员登录入口）
- DRF API 文档：`http://127.0.0.1:8000/docs/`
- JWT 登录接口：`http://127.0.0.1:8000/jwt-auth/`

#### 2.4.3 前端环境配置

进入前端目录：

```bash
cd exam-online
```

安装依赖：

```bash
npm install
```

启动开发服务：

```bash
npm run serve
```

构建生产版本：

```bash
npm run build
```

默认情况下，前端开发服务运行在 `http://localhost:8080/` 附近的端口。
若需要配置反向代理，可在 `vue.config.js` 或 Nginx 配置中将 API 请求代理到后端 `127.0.0.1:8000`。

#### 2.4.4 运行顺序

推荐按以下顺序运行系统：

1. 启动后端服务：`python manage.py runserver`
2. 启动前端服务：`npm run serve`
3. 访问前端页面并注册/登录学生账号
4. 使用 xadmin 后台维护班级、题库、试卷和考试数据
5. 学生报名考试、生成准考证并在线答题
6. 教师进入阅卷页面处理主观题

## 3 遵循的编码规范

### 3.1 总体规范

项目遵循“分层清晰、命名明确、接口稳定、异常可控”的编码原则。
前端按照页面、组件、路由、插件、状态管理分层；
后端按照 Django 应用划分业务边界，并通过模型、序列化器、视图、过滤器、服务函数拆分职责。

总体约定：

- 代码提交前保证项目可以正常启动；
- 新增功能尽量放入对应业务模块，避免跨模块随意堆放；
- 命名应体现业务含义，避免无意义缩写；
- 复杂业务逻辑应拆分为函数或服务层方法；
- 接口返回结构保持稳定，便于前端调用；
- 对用户输入、考试状态、分数范围等关键规则进行校验；
- 数据库结构变更必须配套迁移文件。

### 3.2 Python/Django 编码规范

后端遵循 PEP 8 和 Django 官方推荐风格。

#### 3.2.1 命名规范

- Python 文件、函数、变量使用小写加下划线，例如 `exam_start_at`、`exam_end_at`；
- 类名使用大驼峰命名，例如 `ExamListViewSet`、`GeneratePaperAPIView`；
- 模型类使用单数名词，例如 `Student`、`Exam`、`Paper`；
- 数据表字段使用小写加下划线，例如 `create_time`、`update_time`、`admission_number`；
- URL 路径使用小写单词和连字符/斜杠组织，例如 `/api/paper/generate/`。

#### 3.2.2 分层规范

后端主要分层如下：

- `models.py`：定义数据库模型、字段、关系、模型级校验和保存规则；
- `serializers.py`：定义模型与 JSON 数据之间的转换；
- `views.py`：定义 API 视图、查询过滤、请求参数处理和响应；
- `filter.py`：定义查询过滤条件；
- `services.py`：封装独立业务服务，例如 AI 主观题评分建议；
- `admin.py` / `adminx.py`：配置后台管理展示；
- `migrations/`：保存数据库迁移脚本；
- `tests/`：保存模型、接口和后台配置测试。

#### 3.2.3 业务规则规范

- 考试开始和结束时间统一通过 `exam_start_at`、`exam_end_at` 计算；
- 考试报名必须检查考试是否存在、是否已经开始、是否重复报名；
- 试卷总分由题型数量自动计算，避免手动填写造成不一致；
- 主观题分数必须在 `0` 到题目满分之间；
- 阅卷记录保存前后分数、评语和操作人，方便追踪；
- 题目抽取统一按照科目和难度过滤，避免出现空卷或错科目题目。

#### 3.2.4 异常处理规范

- 对缺少参数的请求返回 `400 Bad Request`；
- 对不存在的资源返回 `404 Not Found`；
- 对数据库迁移未执行导致的表不存在情况返回明确提示；
- 对 AI 辅助评分不可用情况返回 `503` 或隐藏 AI 建议区域，不影响教师人工阅卷；
- 后端对可预期错误返回 JSON 消息，避免直接暴露堆栈信息给前端用户。

### 3.3 前端 Vue 编码规范

前端遵循 Vue 2 单文件组件规范。

#### 3.3.1 文件组织规范

- 页面级组件放在 `src/views`；
- 可复用组件放在 `src/components`；
- 全局布局放在 `src/layout`；
- 路由集中写在 `src/router/index.js`；
- HTTP 请求插件放在 `src/plugins/axios.js`；
- 全局状态放在 `src/store/index.js`；
- 图片资源放在 `src/assets`。

#### 3.3.2 命名规范

- Vue 页面组件使用大驼峰文件名，例如 `Login.vue`、`AdmitCard.vue`；
- 路由 `name` 使用有业务意义的英文单词；
- 组件内方法使用动词或动宾短语；
- 接口字段名称尽量与后端模型字段保持一致，减少转换成本。

#### 3.3.3 交互规范

- 未登录用户访问业务页面时跳转登录页；
- 页面标题通过路由 `meta.title` 统一设置；
- 请求统一通过 Axios 插件发送；
- 请求前自动附加认证头和 CSRF Token；
- 对加载、异常、空数据等状态进行提示；
- 表单提交前做必要的前端校验，后端再做最终校验。

### 3.4 Git 协作规范

建议团队协作时遵循以下 Git 规范：

- `main` 或 `master` 分支保存稳定版本；
- 功能开发使用 `feature/功能名称` 分支；
- 修复问题使用 `fix/问题名称` 分支；
- 每次提交只包含一类相关修改；
- 提交信息使用简短明确的描述。

## 4 数据库实现简介

### 4.1 数据库选型

系统当前使用 SQLite 作为后台数据库，配置位于：

```text
ExamOnline/ExamOnline/settings.py
```

数据库配置如下：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```

SQLite 的优点是配置简单、无需单独安装数据库服务，适合课程实验、单机开发和功能演示。
系统的数据结构由 Django ORM 模型定义，通过迁移脚本自动创建表。

### 4.2 数据库创建与迁移脚本

系统没有手写单独的 `.sql` 初始化文件，而是采用 Django 标准迁移机制管理数据库结构。
迁移脚本位于各应用的 `migrations` 目录：

```text
ExamOnline/user/migrations
ExamOnline/exam/migrations
ExamOnline/question/migrations
ExamOnline/record/migrations
```

主要迁移文件包括：

- `user/migrations/0001_initial.py`：创建班级、学生、教师等用户相关表；
- `user/migrations/0002_student_profile.py`：创建学生扩展资料表；
- `question/migrations/0001_initial.py`：创建选择题、填空题、判断题、主观题表；
- `question/migrations/0002_auto_20260503_1954.py`：补充题目科目等字段；
- `exam/migrations/0001_initial.py`：创建试卷、考试、成绩、练习等表；
- `exam/migrations/0003_auto_20260503_1954.py`：补充考试类别、题目科目等相关结构；
- `exam/migrations/0004_registration_ai_review.py`：创建考试报名、主观题阅卷相关结构；
- `exam/migrations/0005_exam_start_review_history.py`：补充考试开始时间与阅卷历史；
- `exam/migrations/0006_exam_time_range.py`：补充考试结束时间与时长计算；
- `record/migrations/0001_initial.py`：创建各题型练习/答题记录表。

初始化数据库时执行：

```bash
cd ExamOnline
python manage.py migrate
```

如需查看某个迁移文件对应的 SQL，可执行：

```bash
python manage.py sqlmigrate exam 0001
python manage.py sqlmigrate question 0001
python manage.py sqlmigrate user 0001
python manage.py sqlmigrate record 0001
```

如修改模型后需要生成新的迁移脚本：

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4.3 主要数据表说明

#### 4.3.1 用户与班级相关表

| 模型               | 数据表           | 说明                                     |
| ------------------ | ---------------- | ---------------------------------------- |
| `auth_user`      | Django 内置表    | 保存用户名、密码、权限等登录认证信息     |
| `Clazz`          | 默认生成表       | 保存年级、专业、班级                     |
| `Student`        | `user_student` | 保存学生姓名、性别、关联用户、所在班级   |
| `StudentProfile` | 默认生成表       | 保存学生头像等扩展资料                   |
| `Teacher`        | `user_teacher` | 保存教师姓名、性别、职称、学院、关联用户 |

#### 4.3.2 题库相关表

| 模型           | 说明                                                             |
| -------------- | ---------------------------------------------------------------- |
| `Choice`     | 选择题，包含题干、A/B/C/D 选项、正确答案、解析、分值、难度、科目 |
| `Fill`       | 填空题，包含题干、正确答案、解析、分值、难度、科目               |
| `Judge`      | 判断题，包含题干、正确答案、解析、分值、难度、科目               |
| `Subjective` | 主观题，包含题干、答案模板、评分解析、分值、难度、科目           |

#### 4.3.3 考试与成绩相关表

| 模型                        | 数据表        | 说明                                                                                      |
| --------------------------- | ------------- | ----------------------------------------------------------------------------------------- |
| `Paper`                   | 默认生成表    | 保存试卷名称、科目、总分、题型数量、难度                                                  |
| `Exam`                    | `exam_info` | 保存考试名称、类别、专业方向、日期、开始/结束时间、考试时长、关联试卷、考生须知、限制班级 |
| `ExamRegistration`        | 默认生成表    | 保存考试报名记录和准考证号                                                                |
| `Grade`                   | 默认生成表    | 保存学生考试成绩                                                                          |
| `Practice`                | 默认生成表    | 保存学生模拟练习记录                                                                      |
| `SubjectiveAnswer`        | 默认生成表    | 保存学生主观题答案、分数和匿名阅卷标识                                                    |
| `SubjectiveReviewHistory` | 默认生成表    | 保存主观题分数和评语变更历史                                                              |

#### 4.3.4 答题记录相关表

| 模型                 | 说明                              |
| -------------------- | --------------------------------- |
| `ChoiceRecord`     | 保存选择题练习/答题记录           |
| `FillRecord`       | 保存填空题练习/答题记录           |
| `JudgeRecord`      | 保存判断题练习/答题记录           |
| `SubjectiveRecord` | 保存主观题练习/答题记录及输出结果 |

### 4.4 关键表结构示例

以下为根据 Django 模型整理出的主要建表逻辑示例，实际建表以迁移文件为准。

#### 4.4.1 考试表 `exam_info`

```sql
CREATE TABLE exam_info (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    name varchar(50) NOT NULL,
    category varchar(20),
    major varchar(50) NOT NULL,
    exam_date date NOT NULL,
    start_time time NOT NULL,
    end_time time NOT NULL,
    total_time smallint unsigned NOT NULL,
    tips text NOT NULL,
    paper_id integer NOT NULL UNIQUE REFERENCES exam_paper(id)
);
```

说明：

- `paper_id` 与试卷表是一对一关系；
- `start_time`、`end_time` 用于计算考试时长和考试可见状态；
- `category` 用于区分资格认证、课程考试、竞赛选拔等考试类型；
- 限制班级为多对多关系，Django 会额外生成中间表。

#### 4.4.2 试卷表 `exam_paper`

```sql
CREATE TABLE exam_paper (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    name varchar(50) NOT NULL,
    subject varchar(50) NOT NULL,
    score smallint unsigned NOT NULL,
    choice_number smallint unsigned NOT NULL,
    fill_number smallint unsigned NOT NULL,
    judge_number smallint unsigned NOT NULL,
    subjective_number smallint unsigned NOT NULL,
    level varchar(1) NOT NULL
);
```

说明：

- `subject` 用于组卷时匹配题库科目；
- `level` 用于匹配题目难度；
- `score` 由题型数量自动计算。

#### 4.4.3 考试报名表

```sql
CREATE TABLE exam_examregistration (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    admission_number varchar(32) NOT NULL UNIQUE,
    create_time datetime NOT NULL,
    exam_id integer NOT NULL REFERENCES exam_info(id),
    student_id integer NOT NULL REFERENCES user_student(id),
    UNIQUE (exam_id, student_id)
);
```

说明：

- `admission_number` 保存自动生成的准考证号；
- `UNIQUE (exam_id, student_id)` 保证同一学生不能重复报名同一考试。

#### 4.4.4 主观题答案表

```sql
CREATE TABLE exam_subjectiveanswer (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    answer text NOT NULL,
    score smallint unsigned,
    create_time datetime NOT NULL,
    update_time datetime NOT NULL,
    identifier varchar(8) NOT NULL,
    exam_id integer NOT NULL REFERENCES exam_info(id),
    question_id integer NOT NULL REFERENCES question_subjective(id),
    student_id integer NOT NULL REFERENCES user_student(id)
);
```

说明：

- `score` 允许为空，表示尚未阅卷；
- `identifier` 用于关联一次考试提交和匿名阅卷；
- `question_id` 关联主观题题库；
- `student_id` 仅后端保存，阅卷页面使用匿名编号展示。

#### 4.4.5 主观题阅卷历史表

```sql
CREATE TABLE exam_subjectivereviewhistory (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    operator varchar(50) NOT NULL,
    old_score smallint unsigned,
    new_score smallint unsigned,
    old_comment text NOT NULL,
    new_comment text NOT NULL,
    create_time datetime NOT NULL,
    subjective_answer_id integer NOT NULL REFERENCES exam_subjectiveanswer(id)
);
```

说明：

- 记录每次教师保存评分时的分数变化；
- 保存操作人和评语，便于审计和回溯。

### 4.5 数据关系说明

主要关系如下：

- 一个 Django 用户对应一个学生或教师资料；
- 一个学生属于一个班级；
- 一个考试关联一张试卷；
- 一个考试可以限制多个班级；
- 一个学生可以报名多个考试；
- 一个考试可以被多个学生报名；
- 一个学生在一场考试中产生一条或多条成绩/主观题答案记录；
- 一条主观题答案可以对应多条阅卷历史；
- 一次练习可以关联多条选择题、填空题、判断题或主观题答题记录。

可概括为：

```text
User 1---1 Student
Clazz 1---N Student
Paper 1---1 Exam
Exam N---N Clazz
Exam 1---N ExamRegistration N---1 Student
Exam 1---N Grade N---1 Student
Exam 1---N SubjectiveAnswer N---1 Student
SubjectiveAnswer 1---N SubjectiveReviewHistory
Practice 1---N Record
```

### 4.6 数据初始化建议

首次运行系统后，建议按以下顺序在 xadmin 后台初始化基础数据：

1. 创建管理员账号；
2. 创建班级数据；
3. 创建学生用户和学生资料；
4. 创建题库数据，包括选择题、填空题、判断题、主观题；
5. 创建试卷，配置科目、难度和各题型数量；
6. 创建考试，绑定试卷，设置考试日期、开始时间、结束时间和允许班级；
7. 学生登录前台进行报名、查看准考证和参加考试；
8. 教师/管理员进入阅卷页面完成主观题评分。

### 4.7 数据库备份与恢复

由于当前使用 SQLite，数据库文件为：

```text
ExamOnline/db.sqlite3
```

备份时复制该文件即可。恢复时将备份文件放回 `ExamOnline` 目录，并保证迁移文件与数据库结构匹配。

也可以使用 Django 命令导出数据：

```bash
python manage.py dumpdata > data.json
```

恢复数据：

```bash
python manage.py loaddata data.json
```
