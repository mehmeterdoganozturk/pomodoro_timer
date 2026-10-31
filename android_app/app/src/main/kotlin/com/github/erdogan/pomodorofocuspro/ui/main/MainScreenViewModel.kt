package com.github.erdogan.pomodorofocuspro.ui.main

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.github.erdogan.pomodorofocuspro.data.PomodoroRepository
import com.github.erdogan.pomodorofocuspro.engine.TimerEngine
import com.github.erdogan.pomodorofocuspro.model.*
import com.github.erdogan.pomodorofocuspro.widget.PomodoroWidgetProvider
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
    private val _uiState = MutableStateFlow(MainUiState())
    val uiState: StateFlow<MainUiState> = _uiState.asStateFlow()

    init {
        TimerEngine.init(application)
        val cfg = repository.loadConfig()
        val streakPair = repository.calculateStreak(cfg.dailyGoal)
        val heatmap = repository.getLast28Days()
        val engState = TimerEngine.stateFlow.value

        _uiState.value = _uiState.value.copy(
            config = cfg,
            mode = engState.mode,
            state = engState.state,
            remainingSeconds = engState.remainingSeconds,
            totalSeconds = engState.totalSeconds,
            stopwatchSeconds = engState.stopwatchSeconds,
            sessionCount = engState.sessionCount,
            todayRecord = repository.getRecordForDate(repository.getTodayDateStr()),
            streak = streakPair.first,
            bestStreak = streakPair.second,
            heatmapDays = heatmap
        )

        // Observe TimerEngine
        viewModelScope.launch {
            TimerEngine.stateFlow.collect { engineState ->
                _uiState.value = _uiState.value.copy(
                    mode = engineState.mode,
                    state = engineState.state,
                    remainingSeconds = engineState.remainingSeconds,
                    totalSeconds = engineState.totalSeconds,
                    stopwatchSeconds = engineState.stopwatchSeconds,
                    sessionCount = engineState.sessionCount
                )
            }
        }

        // Observe Config changes
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

        // Observe Today Record changes
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
        TimerEngine.switchMode(getApplication(), newMode)
    }

    fun setTestPreset(minutes: Int) {
        TimerEngine.setTestPreset(getApplication(), minutes)
    }

    fun toggleStartPause() {
        TimerEngine.toggleStartPause(getApplication())
    }

    fun start() {
        TimerEngine.start(getApplication())
    }

    fun pause() {
        TimerEngine.pause(getApplication())
    }

    fun reset() {
        TimerEngine.reset(getApplication())
    }

    fun skipNext() {
        TimerEngine.skipNext(getApplication())
    }

    fun selectProfile(profileId: String) {
        val cfg = _uiState.value.config
        val profile = cfg.profiles[profileId] ?: return
        val firstSub = profile.subjects.firstOrNull()?.id ?: ""
        val updated = cfg.copy(activeProfileId = profileId, selectedSubjectId = firstSub)
        repository.saveConfig(updated)
        PomodoroWidgetProvider.updateAllWidgets(getApplication())
    }

    fun selectSubject(subjectId: String) {
        val cfg = _uiState.value.config.copy(selectedSubjectId = subjectId)
        repository.saveConfig(cfg)
        PomodoroWidgetProvider.updateAllWidgets(getApplication())
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
        PomodoroWidgetProvider.updateAllWidgets(getApplication())
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
        PomodoroWidgetProvider.updateAllWidgets(getApplication())
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
        PomodoroWidgetProvider.updateAllWidgets(getApplication())
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

        // If stopped, refresh duration in TimerEngine
        if (_uiState.value.state == TimerState.STOPPED) {
            TimerEngine.switchMode(getApplication(), _uiState.value.mode)
        }
        PomodoroWidgetProvider.updateAllWidgets(getApplication())
    }
}
