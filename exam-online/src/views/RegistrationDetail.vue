<template>
    <div class="registration-detail">
        <el-card class="box-card">
            <div slot="header" class="clearfix">
                <span>报名详情</span>
                <el-button style="float: right; padding: 3px 0" type="text" @click="$router.push('/exam')">返回</el-button>
            </div>
            <div v-if="exam" class="info-content">
                <p><strong>考试名称：</strong>{{ exam.name }}</p>
                <p><strong>考试日期：</strong>{{ exam.exam_date }}</p>
                <p><strong>考试时长：</strong>{{ exam.total_time }} 分钟</p>
                <p><strong>所属专业：</strong>{{ exam.major }}</p>
                <p><strong>考生须知：</strong></p>
                <div class="tips">{{ exam.tips }}</div>
                
                <el-divider></el-divider>
                
                <el-button type="primary" @click="applyRegistration" :loading="loading">立即报名</el-button>
            </div>
        </el-card>
    </div>
</template>

<script>
export default {
    name: "RegistrationDetail",
    data() {
        return {
            exam: null,
            loading: false
        }
    },
    created() {
        // 假设通过路由查询参数传递了考试ID
        const examId = this.$route.query.id;
        if (examId) {
            this.fetchExamDetail(examId);
        } else {
            this.$message.error('未找到指定的考试！');
            this.$router.push('/exam');
        }
    },
    methods: {
        fetchExamDetail(id) {
            this.$axios.get(`/api/exams/${id}/?format=json`).then(res => {
                this.exam = res.data;
            }).catch(err => {
                this.$message.error('获取考试详情失败');
            });
        },
        applyRegistration() {
            this.loading = true;
            this.$axios.post(`/api/registrations/?format=json`, {
                exam: this.exam.id
            }).then(res => {
                this.$message.success('报名申请提交成功，请等待审核！');
                this.$router.push('/my-registrations');
            }).catch(err => {
                if(err.response && err.response.status === 400) {
                    this.$message.warning('您已经报名过该考试，无需重复报名！');
                } else {
                    this.$message.error('报名失败，请重试');
                }
            }).finally(() => {
                this.loading = false;
            });
        }
    }
}
</script>

<style scoped>
.registration-detail {
    margin-top: 20px;
}
.info-content {
    line-height: 2.0;
    font-size: 16px;
}
.tips {
    background-color: #f5f7fa;
    padding: 15px;
    border-radius: 4px;
    margin-top: 10px;
}
</style>