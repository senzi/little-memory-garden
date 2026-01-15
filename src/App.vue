<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import HistoryPanel from './components/HistoryPanel.vue'

const TOTAL_ROUNDS = 5
const OBSERVE_SECONDS = 8
const DATA_PATH = '/data/questions.jsonl'
const STATS_KEY = 'lmg_stats_v1'

const state = ref('loading')
const errorMessage = ref('')
const bank = ref([])
const rounds = ref([])
const currentRoundIndex = ref(0)
const currentQuestion = ref(null)
const selectedOption = ref(null)
const isCorrect = ref(false)
const countdown = ref(OBSERVE_SECONDS)
const totalScore = ref(0)
const correctCount = ref(0)
const roundScores = ref([])
const totalPossible = ref(0)
const stats = ref({
  totalGames: 0,
  totalCorrect: 0,
  totalQuestions: 0,
  totalScore: 0,
  totalPossible: 0,
})

let countdownTimer = null
let observeTimer = null

const currentEntry = computed(() => rounds.value[currentRoundIndex.value] || null)
const roundNumberLabel = computed(() => `第 ${currentRoundIndex.value + 1} / ${TOTAL_ROUNDS} 轮`)
const answerText = computed(() => {
  if (!currentQuestion.value) return ''
  return currentQuestion.value.options[currentQuestion.value.answer] || ''
})
const feedbackText = computed(() =>
  isCorrect.value
    ? '真棒！你记得很清楚。'
    : '再仔细看看就更棒啦～'
)
const canStart = computed(() => bank.value.length > 0)
const averageRoundScore = computed(() => (totalScore.value / TOTAL_ROUNDS).toFixed(1))
const overallAccuracy = computed(() => {
  if (stats.value.totalQuestions === 0) return '0%'
  const rate = (stats.value.totalCorrect / stats.value.totalQuestions) * 100
  return `${Math.round(rate)}%`
})

const clearTimers = () => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
  if (observeTimer) {
    clearTimeout(observeTimer)
    observeTimer = null
  }
}

const shuffle = (list) => {
  const result = [...list]
  for (let i = result.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[result[i], result[j]] = [result[j], result[i]]
  }
  return result
}

const parseBank = (text) => {
  const lines = text.split(/\r?\n/).filter((line) => line.trim())
  const items = []
  for (const line of lines) {
    try {
      const item = JSON.parse(line)
      if (validateEntry(item)) items.push(item)
    } catch (err) {
      continue
    }
  }
  return items
}

const validateEntry = (entry) => {
  if (!entry || typeof entry !== 'object') return false
  if (!entry.image || !Array.isArray(entry.questions) || entry.questions.length === 0) return false
  const validQuestions = entry.questions.filter((question) => {
    if (!question || typeof question !== 'object') return false
    if (!question.text || !Array.isArray(question.options) || question.options.length < 2) return false
    const answer = Number(question.answer)
    const difficulty = Number(question.difficulty)
    if (!Number.isFinite(answer) || !Number.isFinite(difficulty)) return false
    if (answer < 0 || answer >= question.options.length) return false
    return true
  })
  entry.questions = validQuestions
  return entry.questions.length > 0
}

const loadStats = () => {
  try {
    const raw = localStorage.getItem(STATS_KEY)
    if (!raw) return
    const parsed = JSON.parse(raw)
    stats.value = {
      totalGames: Number(parsed.totalGames) || 0,
      totalCorrect: Number(parsed.totalCorrect) || 0,
      totalQuestions: Number(parsed.totalQuestions) || 0,
      totalScore: Number(parsed.totalScore) || 0,
      totalPossible: Number(parsed.totalPossible) || 0,
    }
  } catch (err) {
    stats.value = { totalGames: 0, totalCorrect: 0, totalQuestions: 0, totalScore: 0, totalPossible: 0 }
  }
}

const saveStats = () => {
  localStorage.setItem(STATS_KEY, JSON.stringify(stats.value))
}

const updateStats = () => {
  stats.value.totalGames += 1
  stats.value.totalCorrect += correctCount.value
  stats.value.totalQuestions += TOTAL_ROUNDS
  stats.value.totalScore += totalScore.value
  stats.value.totalPossible += totalPossible.value
  saveStats()
}

const clearStats = () => {
  stats.value = { totalGames: 0, totalCorrect: 0, totalQuestions: 0, totalScore: 0, totalPossible: 0 }
  localStorage.removeItem(STATS_KEY)
}

const loadBank = async () => {
  try {
    const response = await fetch(DATA_PATH)
    if (!response.ok) throw new Error('题库加载失败')
    const text = await response.text()
    const items = parseBank(text)
    if (!items.length) throw new Error('题库为空或格式不正确')
    bank.value = items
    state.value = 'start'
  } catch (err) {
    errorMessage.value = err.message || '题库加载失败'
    state.value = 'error'
  }
}

const buildRounds = () => {
  if (bank.value.length >= TOTAL_ROUNDS) {
    return shuffle(bank.value).slice(0, TOTAL_ROUNDS)
  }
  const result = []
  while (result.length < TOTAL_ROUNDS) {
    result.push(bank.value[result.length % bank.value.length])
  }
  return shuffle(result)
}

const prepareRound = () => {
  const entry = currentEntry.value
  if (!entry) return
  const question = shuffle(entry.questions)[0]
  currentQuestion.value = question
  selectedOption.value = null
  isCorrect.value = false
}

const startGame = () => {
  if (!canStart.value) return
  rounds.value = buildRounds()
  currentRoundIndex.value = 0
  totalScore.value = 0
  correctCount.value = 0
  roundScores.value = []
  totalPossible.value = 0
  prepareRound()
  state.value = 'ready'
}

const startObserve = () => {
  clearTimers()
  countdown.value = OBSERVE_SECONDS
  state.value = 'observe'
  countdownTimer = setInterval(() => {
    if (countdown.value > 1) {
      countdown.value -= 1
    }
  }, 1000)
  observeTimer = setTimeout(() => {
    clearTimers()
    state.value = 'quiz'
  }, OBSERVE_SECONDS * 1000)
}

const chooseOption = (index) => {
  if (selectedOption.value !== null) return
  selectedOption.value = index
  isCorrect.value = index === currentQuestion.value.answer
  const score = isCorrect.value ? Number(currentQuestion.value.difficulty) : 0
  roundScores.value[currentRoundIndex.value] = score
  totalScore.value += score
  totalPossible.value += Number(currentQuestion.value.difficulty)
  if (isCorrect.value) correctCount.value += 1
  state.value = 'feedback'
}

const nextStep = () => {
  if (currentRoundIndex.value < TOTAL_ROUNDS - 1) {
    currentRoundIndex.value += 1
    prepareRound()
    state.value = 'ready'
  } else {
    updateStats()
    state.value = 'summary'
  }
}

const restartGame = () => {
  startGame()
}

const openHistory = () => {
  state.value = 'history'
}

const backToStart = () => {
  state.value = 'start'
}

onMounted(() => {
  loadStats()
  loadBank()
})

onBeforeUnmount(() => {
  clearTimers()
})
</script>

<template>
  <div class="page">
    <header class="topbar">
      <div class="brand">记忆小花园</div>
      <div class="tag">离线专注训练</div>
    </header>

    <main class="panel">
      <section v-if="state === 'loading'" class="section fade">
        <h1>正在准备题库</h1>
        <p>请稍等，我们正在打开记忆花园。</p>
      </section>

      <section v-else-if="state === 'error'" class="section fade">
        <h1>题库还没准备好</h1>
        <p>{{ errorMessage }}</p>
        <p>请检查 `public/data/questions.jsonl` 是否存在并填写内容。</p>
      </section>

      <section v-else-if="state === 'start'" class="section start">
        <div class="start-hero">
          <h1>一起开启观察力挑战</h1>
          <p>每一轮先看一张图，再回答一个小问题，温柔练习专注与记忆。</p>
        </div>
        <div class="rules">
          <div>
            <strong>游戏流程</strong>
            <span>共 5 轮，每轮先观察 8 秒，再答 1 道题。</span>
          </div>
          <div>
            <strong>答题节奏</strong>
            <span>没有倒计时，想好再选。</span>
          </div>
          <div>
            <strong>得分方式</strong>
            <span>答对得到对应难度分，答错记 0 分。</span>
          </div>
        </div>
        <div class="stat-box">
          <h3>历史小记录</h3>
          <div class="stat-grid">
            <div>
              <p>已完成局数</p>
              <strong>{{ stats.totalGames }}</strong>
            </div>
            <div>
              <p>整体正确率</p>
              <strong>{{ overallAccuracy }}</strong>
            </div>
            <div>
              <p>平均每局得分</p>
              <strong>{{ stats.totalGames ? (stats.totalScore / stats.totalGames).toFixed(1) : '0.0' }}</strong>
            </div>
          </div>
        </div>
        <div class="actions">
          <button class="primary" @click="startGame">开始游戏</button>
          <button class="ghost" @click="openHistory">查看记录</button>
        </div>
      </section>

      <section v-else-if="state === 'ready'" class="section fade">
        <div class="round-head">
          <p class="round-label">{{ roundNumberLabel }}</p>
          <div class="progress">
            <span
              v-for="(_, index) in TOTAL_ROUNDS"
              :key="index"
              :class="['dot', { active: index <= currentRoundIndex }]"
            ></span>
          </div>
        </div>
        <h2>准备好观察了吗？</h2>
        <p>点一下按钮，我们就开始展示图片。</p>
        <button class="primary" @click="startObserve">准备好了</button>
      </section>

      <section v-else-if="state === 'observe'" class="section observe">
        <div class="round-head">
          <p class="round-label">{{ roundNumberLabel }}</p>
          <div class="countdown">{{ countdown }} 秒</div>
        </div>
        <div class="image-frame">
          <img :src="currentEntry.image" :alt="currentEntry.description || '观察图片'" />
        </div>
        <p class="hint">认真看看颜色、数量和小细节。</p>
      </section>

      <section v-else-if="state === 'quiz'" class="section quiz">
        <div class="round-head">
          <p class="round-label">{{ roundNumberLabel }}</p>
        </div>
        <h2>{{ currentQuestion.text }}</h2>
        <div class="options">
          <button
            v-for="(option, index) in currentQuestion.options"
            :key="option"
            class="option"
            @click="chooseOption(index)"
          >
            {{ option }}
          </button>
        </div>
      </section>

      <section v-else-if="state === 'feedback'" class="section feedback">
        <div class="round-head">
          <p class="round-label">{{ roundNumberLabel }}</p>
        </div>
        <div class="image-frame small">
          <img :src="currentEntry.image" :alt="currentEntry.description || '观察图片'" />
        </div>
        <h2>{{ feedbackText }}</h2>
        <p>正确答案：{{ answerText }}</p>
        <p>本轮得分：{{ roundScores[currentRoundIndex] || 0 }}</p>
        <button class="primary" @click="nextStep">
          {{ currentRoundIndex < TOTAL_ROUNDS - 1 ? '准备好了' : '查看结算' }}
        </button>
      </section>

      <section v-else-if="state === 'summary'" class="section summary">
        <h1>本局完成啦</h1>
        <div class="summary-grid">
          <div>
            <p>答对题数</p>
            <strong>{{ correctCount }} / {{ TOTAL_ROUNDS }}</strong>
          </div>
          <div>
            <p>本局总得分</p>
            <strong>{{ totalScore }}</strong>
          </div>
          <div>
            <p>本局平均得分</p>
            <strong>{{ averageRoundScore }}</strong>
          </div>
        </div>
        <div class="stat-box">
          <h3>累计统计</h3>
          <div class="stat-grid">
            <div>
              <p>已完成局数</p>
              <strong>{{ stats.totalGames }}</strong>
            </div>
            <div>
              <p>整体正确率</p>
              <strong>{{ overallAccuracy }}</strong>
            </div>
            <div>
              <p>累计得分占比</p>
              <strong>{{ stats.totalPossible ? Math.round((stats.totalScore / stats.totalPossible) * 100) : 0 }}%</strong>
            </div>
          </div>
        </div>
        <div class="actions">
          <button class="primary" @click="restartGame">再来一局</button>
          <button class="ghost" @click="openHistory">查看记录</button>
        </div>
      </section>

      <section v-else-if="state === 'history'" class="section history">
        <HistoryPanel
          :stats="stats"
          @back="backToStart"
          @clear="clearStats"
        />
      </section>
    </main>

    <footer class="foot">
      <p>温柔观察 · 慢慢记住 · 每一轮都在进步</p>
    </footer>
  </div>
</template>
