<script setup>
const props = defineProps({
  stats: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['back', 'clear'])

const handleClear = () => {
  emit('clear')
}
</script>

<template>
  <div class="history-panel">
    <div class="history-head">
      <h1>历史记录</h1>
      <p>这里可以查看累计统计，并管理本地记录。</p>
    </div>
    <div class="stat-box">
      <div class="stat-grid">
        <div>
          <p>已完成局数</p>
          <strong>{{ stats.totalGames }}</strong>
        </div>
        <div>
          <p>累计正确数</p>
          <strong>{{ stats.totalCorrect }}</strong>
        </div>
        <div>
          <p>累计题目数</p>
          <strong>{{ stats.totalQuestions }}</strong>
        </div>
        <div>
          <p>累计得分占比</p>
          <strong>{{ stats.totalPossible ? Math.round((stats.totalScore / stats.totalPossible) * 100) : 0 }}%</strong>
        </div>
        <div>
          <p>平均每局得分</p>
          <strong>{{ stats.totalGames ? (stats.totalScore / stats.totalGames).toFixed(1) : '0.0' }}</strong>
        </div>
        <div>
          <p>总体正确率</p>
          <strong>{{ stats.totalQuestions ? Math.round((stats.totalCorrect / stats.totalQuestions) * 100) : 0 }}%</strong>
        </div>
      </div>
    </div>
    <div class="actions">
      <button class="primary" @click="emit('back')">返回开始</button>
      <button class="ghost" @click="handleClear">清空记录</button>
    </div>
  </div>
</template>
