<template>
    <div class="my-registrations">
        <el-card>
            <div slot="header">
                <span>我的报名记录</span>
            </div>
            <el-table :data="tableData" style="width: 100%" v-loading="loading">
                <el-table-column prop="exam_info.name" label="考试名称" width="250"></el-table-column>
                <el-table-column prop="exam_info.exam_date" label="考试日期"></el-table-column>
                <el-table-column label="申请时间" width="200">
                    <template slot-scope="scope">
                        {{ formatDate(scope.row.apply_time) }}
                    </template>
                </el-table-column>
                <el-table-column label="状态">
                    <template slot-scope="scope">
                        <el-tag v-if="scope.row.status === '0'" type="warning">待审核</el-tag>
                        <el-tag v-if="scope.row.status === '1'" type="success">已通过</el-tag>
                        <el-tag v-if="scope.row.status === '2'" type="danger">已拒绝</el-tag>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>
    </div>
</template>

<script>
export default {
    name: "MyRegistrations",
    data() {
        return {
            tableData: [],
            loading: false
        }
    },
    created() {
        this.fetchRegistrations();
    },
    methods: {
        fetchRegistrations() {
            this.loading = true;
            this.$axios.get(`/api/registrations/?format=json`).then(res => {
                this.tableData = res.data.results || res.data;
            }).catch(err => {
                this.$message.error('获取报名记录失败');
            }).finally(() => {
                this.loading = false;
            });
        },
        formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleString();
        }
    }
}
</script>

<style scoped>
.my-registrations {
    margin-top: 20px;
}
</style>