<script setup>
import { ref } from 'vue'

defineProps({
  stats: {
    type: Object,
    required: true,
  },
  bankImageCount: {
    type: Number,
    required: true,
  },
  bankQuestionCount: {
    type: Number,
    required: true,
  },
})

const emit = defineEmits(['back', 'clear'])
const confirmClear = ref(false)

const requestClear = () => {
  confirmClear.value = true
}

const cancelClear = () => {
  confirmClear.value = false
}

const confirmClearAction = () => {
  emit('clear')
  confirmClear.value = false
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
    <div class="history-list">
      <h2>单局成绩</h2>
      <div v-if="!stats.gameHistory.length" class="history-empty">暂无记录。</div>
      <div v-else class="history-rows">
        <div v-for="(item, index) in stats.gameHistory" :key="item.id" class="history-row">
          <span>第 {{ stats.totalGames - index }} 局</span>
          <span>得分 {{ item.score }} / {{ item.possible }}</span>
          <span>正确 {{ item.correct }} / {{ item.total }}</span>
        </div>
      </div>
    </div>
    <div class="history-bank">
      <h2>题库统计</h2>
      <p>共有 {{ bankImageCount }} 张图片，合计 {{ bankQuestionCount }} 道题目。</p>
    </div>
    <div class="actions">
      <button class="primary" @click="emit('back')">返回开始</button>
      <div class="inline-confirm">
        <button class="ghost" @click="requestClear">清空记录</button>
        <div v-if="confirmClear" class="confirm-box">
          <span>确定清空？</span>
          <button class="danger" @click="confirmClearAction">确定</button>
          <button class="ghost" @click="cancelClear">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>
