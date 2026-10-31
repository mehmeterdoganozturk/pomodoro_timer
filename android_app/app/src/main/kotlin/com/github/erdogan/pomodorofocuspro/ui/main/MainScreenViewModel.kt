package com.github.erdogan.pomodorofocuspro.ui.main

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.github.erdogan.pomodorofocuspro.data.PomodoroRepository
import com.github.erdogan.pomodorofocuspro.model.*
import com.github.erdogan.pomodorofocuspro.util.SoundHelper
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.util.Date

data class MainUiState(
    val selectedTab: Int = 0, // 0: Sayaç, 1: Zinciri Kırma, 2: Modlar / Dersler
    val mode: TimerMode = TimerMode.POMODORO,
    val state: TimerState = TimerState.STOPPED,
    val remainingSeconds: Int = 25 * 60,
    val totalSeconds: Int = 25 * 60,
    val stopwatchSeconds: Int = 0,
    val sessionCount: Int = 0,
    val config: PomodoroConfig = PomodoroConfig(),
    val todayRecord: DailyRecord = DailyRecord(date = ""),
    val streak: Int = 0,
    val bestStreak: Int = 0,
    val heatmapDays: List<Pair<Date, DailyRecord>> = emptyList(),
    val isSettingsOpen: Boolean = false,
    val isAddSubjectOpen: Boolean = false
) {
    val progressRatio: Float
        get() {
            if (mode == TimerMode.STOPWATCH) {
                return (stopwatchSeconds % 60) / 60f
            }
            if (totalSeconds <= 0) return 0f
            val elapsed = totalSeconds - remainingSeconds
            return (elapsed.toFloat() / totalSeconds.toFloat()).coerceIn(0f, 1f)
        }

    val formattedTime: String
        get() {
            return if (mode == TimerMode.STOPWATCH) {
                val m = stopwatchSeconds / 60
                val s = stopwatchSeconds % 60
                String.format("%02d:%02d", m, s)
            } else {
                val m = remainingSeconds / 60
                val s = remainingSeconds % 60
                String.format("%02d:%02d", m, s)
            }
        }

    val activeProfile: WorkspaceProfile?
        get() = config.profiles[config.activeProfileId] ?: config.profiles.values.firstOrNull()

    val activeSubject: Subject?
        get() = activeProfile?.subjects?.find { it.id == config.selectedSubjectId }
            ?: activeProfile?.subjects?.firstOrNull()
}

class MainScreenViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = PomodoroRepository(application)
    private val soundHelper = SoundHelper(application)

    private val _uiState = MutableStateFlow(MainUiState())
    val uiState: StateFlow<MainUiState> = _uiState.asStateFlow()

    private var timerJob: Job? = null

    init {
        val cfg = repository.loadConfig()
        val streakPair = repository.calculateStreak(cfg.dailyGoal)
        val heatmap = repository.getLast28Days()

        _uiState.value = _uiState.value.copy(
            config = cfg,
            remainingSeconds = cfg.focusDuration * 60,
            totalSeconds = cfg.focusDuration * 60,
            todayRecord = repository.getRecordForDate(repository.getTodayDateStr()),
            streak = streakPair.first,
            bestStreak = streakPair.second,
            heatmapDays = heatmap
        )

        viewModelScope.launch {
            repository.configFlow.collect { newCfg ->
                val streak = repository.calculateStreak(newCfg.dailyGoal)
                _uiState.value = _uiState.value.copy(
                    config = newCfg,
                    streak = streak.first,
                    bestStreak = streak.second
                )
            }
        }

        viewModelScope.launch {
            repository.todayRecordFlow.collect { record ->
                val streak = repository.calculateStreak(_uiState.value.config.dailyGoal)
                _uiState.value = _uiState.value.copy(
                    todayRecord = record,
                    streak = streak.first,
                    bestStreak = streak.second,
                    heatmapDays = repository.getLast28Days()
                )
            }
        }
    }

    fun selectTab(tabIndex: Int) {
        _uiState.value = _uiState.value.copy(selectedTab = tabIndex)
    }

    fun setSettingsOpen(open: Boolean) {
        _uiState.value = _uiState.value.copy(isSettingsOpen = open)
    }

    fun setAddSubjectOpen(open: Boolean) {
        _uiState.value = _uiState.value.copy(isAddSubjectOpen = open)
    }

    fun switchMode(newMode: TimerMode) {
        pause()
        val dur = getDurationForMode(newMode)
        _uiState.value = _uiState.value.copy(
            mode = newMode,
            state = TimerState.STOPPED,
            totalSeconds = dur,
            remainingSeconds = dur,
            stopwatchSeconds = 0
        )
    }

    fun setTestPreset(minutes: Int) {
        pause()
        val sec = minutes * 60
        _uiState.value = _uiState.value.copy(
            mode = TimerMode.TEST,
            state = TimerState.STOPPED,
            totalSeconds = sec,
            remainingSeconds = sec
        )
    }

    private fun getDurationForMode(mode: TimerMode): Int {
        val cfg = _uiState.value.config
        return when (mode) {
            TimerMode.POMODORO -> cfg.focusDuration * 60
            TimerMode.TEST -> cfg.testDuration * 60
            TimerMode.SHORT_BREAK -> cfg.shortBreakDuration * 60
            TimerMode.LONG_BREAK -> cfg.longBreakDuration * 60
            TimerMode.STOPWATCH -> 0
        }
    }

    fun toggleStartPause() {
        if (_uiState.value.state == TimerState.RUNNING) {
            pause()
        } else {
            start()
        }
    }

    fun start() {
        if (_uiState.value.state == TimerState.RUNNING) return
        _uiState.value = _uiState.value.copy(state = TimerState.RUNNING)

        timerJob?.cancel()
        timerJob = viewModelScope.launch {
            while (_uiState.value.state == TimerState.RUNNING) {
                delay(1000L)
                tick()
            }
        }
    }

    fun pause() {
        timerJob?.cancel()
        timerJob = null
        _uiState.value = _uiState.value.copy(state = TimerState.PAUSED)
    }

    fun reset() {
        pause()
        val dur = getDurationForMode(_uiState.value.mode)
        _uiState.value = _uiState.value.copy(
            state = TimerState.STOPPED,
            totalSeconds = dur,
            remainingSeconds = dur,
            stopwatchSeconds = 0
        )
    }

    fun skipNext() {
        pause()
        when (_uiState.value.mode) {
            TimerMode.POMODORO, TimerMode.TEST -> {
                val nextCount = _uiState.value.sessionCount + 1
                val isLong = nextCount % _uiState.value.config.longBreakInterval == 0
                val nextMode = if (isLong) TimerMode.LONG_BREAK else TimerMode.SHORT_BREAK
                _uiState.value = _uiState.value.copy(sessionCount = nextCount)
                switchMode(nextMode)
            }
            TimerMode.SHORT_BREAK, TimerMode.LONG_BREAK, TimerMode.STOPWATCH -> {
                switchMode(TimerMode.POMODORO)
            }
        }
    }

    private fun tick() {
        val current = _uiState.value

        if (current.mode == TimerMode.STOPWATCH) {
            _uiState.value = current.copy(stopwatchSeconds = current.stopwatchSeconds + 1)
            return
        }

        if (current.remainingSeconds > 1) {
            _uiState.value = current.copy(remainingSeconds = current.remainingSeconds - 1)
        } else {
            // Time complete!
            onTimerComplete()
        }
    }

    private fun onTimerComplete() {
        val current = _uiState.value
        val completedMode = current.mode
        val subjectId = current.activeSubject?.id ?: "genel"
        val durMins = current.totalSeconds / 60

        // 1. Record in DB / stats
        repository.recordCompletedSession(completedMode, subjectId, durMins)

        // 2. Play sound & vibrate
        if (completedMode == TimerMode.POMODORO || completedMode == TimerMode.TEST) {
            soundHelper.playFocusComplete(current.config.soundEnabled, current.config.vibrateEnabled)
        } else {
            soundHelper.playBreakComplete(current.config.soundEnabled, current.config.vibrateEnabled)
        }

        // 3. Move to next mode
        if (completedMode == TimerMode.POMODORO || completedMode == TimerMode.TEST) {
            val newSessionCount = current.sessionCount + 1
            val isLong = newSessionCount % current.config.longBreakInterval == 0
            val nextMode = if (isLong) TimerMode.LONG_BREAK else TimerMode.SHORT_BREAK
            val nextDur = getDurationForMode(nextMode)

            _uiState.value = current.copy(
                sessionCount = newSessionCount,
                mode = nextMode,
                state = if (current.config.autoStartBreaks) TimerState.RUNNING else TimerState.STOPPED,
                totalSeconds = nextDur,
                remainingSeconds = nextDur
            )

            if (current.config.autoStartBreaks) {
                start()
            } else {
                pause()
            }
        } else {
            // Break ended -> Back to focus
            val focusDur = getDurationForMode(TimerMode.POMODORO)
            _uiState.value = current.copy(
                mode = TimerMode.POMODORO,
                state = if (current.config.autoStartPomodoros) TimerState.RUNNING else TimerState.STOPPED,
                totalSeconds = focusDur,
                remainingSeconds = focusDur
            )

            if (current.config.autoStartPomodoros) {
                start()
            } else {
                pause()
            }
        }
    }

    fun selectProfile(profileId: String) {
        val cfg = _uiState.value.config
        val profile = cfg.profiles[profileId] ?: return
        val firstSub = profile.subjects.firstOrNull()?.id ?: ""
        val updated = cfg.copy(activeProfileId = profileId, selectedSubjectId = firstSub)
        repository.saveConfig(updated)
    }

    fun selectSubject(subjectId: String) {
        val cfg = _uiState.value.config.copy(selectedSubjectId = subjectId)
        repository.saveConfig(cfg)
    }

    fun addSubject(profileId: String, name: String, icon: String, colorHex: String, badge: String) {
        val cfg = _uiState.value.config
        val profile = cfg.profiles[profileId] ?: return
        val newSub = Subject(
            id = "sub_${System.currentTimeMillis()}",
            name = name,
            icon = icon.ifBlank { "📚" },
            colorHex = colorHex.ifBlank { "#3B82F6" },
            badge = badge.ifBlank { "Genel" },
            visible = true
        )
        val updatedSubs = profile.subjects + newSub
        val updatedProfile = profile.copy(subjects = updatedSubs)
        val updatedProfiles = cfg.profiles.toMutableMap()
        updatedProfiles[profileId] = updatedProfile

        repository.saveConfig(cfg.copy(profiles = updatedProfiles, selectedSubjectId = newSub.id))
    }

    fun deleteSubject(profileId: String, subjectId: String) {
        val cfg = _uiState.value.config
        val profile = cfg.profiles[profileId] ?: return
        val updatedSubs = profile.subjects.filter { it.id != subjectId }
        val updatedProfile = profile.copy(subjects = updatedSubs)
        val updatedProfiles = cfg.profiles.toMutableMap()
        updatedProfiles[profileId] = updatedProfile

        val nextSelected = if (cfg.selectedSubjectId == subjectId) {
            updatedSubs.firstOrNull()?.id ?: ""
        } else {
            cfg.selectedSubjectId
        }

        repository.saveConfig(cfg.copy(profiles = updatedProfiles, selectedSubjectId = nextSelected))
    }

    fun toggleSubjectVisibility(profileId: String, subjectId: String) {
        val cfg = _uiState.value.config
        val profile = cfg.profiles[profileId] ?: return
        val updatedSubs = profile.subjects.map {
            if (it.id == subjectId) it.copy(visible = !it.visible) else it
        }
        val updatedProfile = profile.copy(subjects = updatedSubs)
        val updatedProfiles = cfg.profiles.toMutableMap()
        updatedProfiles[profileId] = updatedProfile

        repository.saveConfig(cfg.copy(profiles = updatedProfiles))
    }

    fun saveSettings(
        focusDur: Int,
        testDur: Int,
        shortDur: Int,
        longDur: Int,
        longInterval: Int,
        goal: Int,
        sound: Boolean,
        vibrate: Boolean,
        autoBreaks: Boolean,
        autoPomodoros: Boolean
    ) {
        val cfg = _uiState.value.config.copy(
            focusDuration = focusDur,
            testDuration = testDur,
            shortBreakDuration = shortDur,
            longBreakDuration = longDur,
            longBreakInterval = longInterval,
            dailyGoal = goal,
            soundEnabled = sound,
            vibrateEnabled = vibrate,
            autoStartBreaks = autoBreaks,
            autoStartPomodoros = autoPomodoros
        )
        repository.saveConfig(cfg)

        // If stopped, refresh duration
        if (_uiState.value.state == TimerState.STOPPED) {
            val d = getDurationForMode(_uiState.value.mode)
            _uiState.value = _uiState.value.copy(totalSeconds = d, remainingSeconds = d)
        }
    }
}
