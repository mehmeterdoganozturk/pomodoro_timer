package com.github.erdogan.pomodorofocuspro.engine

import android.content.Context
import android.content.Intent
import com.github.erdogan.pomodorofocuspro.data.PomodoroRepository
import com.github.erdogan.pomodorofocuspro.model.DailyRecord
import com.github.erdogan.pomodorofocuspro.model.PomodoroConfig
import com.github.erdogan.pomodorofocuspro.model.TimerMode
import com.github.erdogan.pomodorofocuspro.model.TimerState
import com.github.erdogan.pomodorofocuspro.service.TimerService
import com.github.erdogan.pomodorofocuspro.util.SoundHelper
import com.github.erdogan.pomodorofocuspro.widget.PomodoroWidgetProvider
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

data class TimerEngineState(
    val mode: TimerMode = TimerMode.POMODORO,
    val state: TimerState = TimerState.STOPPED,
    val remainingSeconds: Int = 25 * 60,
    val totalSeconds: Int = 25 * 60,
    val stopwatchSeconds: Int = 0,
    val sessionCount: Int = 0
) {
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
}

object TimerEngine {

    private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    private var timerJob: Job? = null

    private val _stateFlow = MutableStateFlow(TimerEngineState())
    val stateFlow: StateFlow<TimerEngineState> = _stateFlow.asStateFlow()

    private var repository: PomodoroRepository? = null
    private var soundHelper: SoundHelper? = null

    fun init(context: Context) {
        if (repository == null) {
            val appCtx = context.applicationContext
            repository = PomodoroRepository(appCtx)
            soundHelper = SoundHelper(appCtx)

            val cfg = repository!!.loadConfig()
            val dur = cfg.focusDuration * 60
            _stateFlow.value = _stateFlow.value.copy(
                remainingSeconds = dur,
                totalSeconds = dur
            )
        }
    }

    private fun getRepo(context: Context): PomodoroRepository {
        init(context)
        return repository!!
    }

    private fun getSound(context: Context): SoundHelper {
        init(context)
        return soundHelper!!
    }

    fun getDurationForMode(config: PomodoroConfig, mode: TimerMode): Int {
        return when (mode) {
            TimerMode.POMODORO -> config.focusDuration * 60
            TimerMode.TEST -> config.testDuration * 60
            TimerMode.SHORT_BREAK -> config.shortBreakDuration * 60
            TimerMode.LONG_BREAK -> config.longBreakDuration * 60
            TimerMode.STOPWATCH -> 0
        }
    }

    fun toggleStartPause(context: Context) {
        if (_stateFlow.value.state == TimerState.RUNNING) {
            pause(context)
        } else {
            start(context)
        }
    }

    fun start(context: Context) {
        init(context)
        if (_stateFlow.value.state == TimerState.RUNNING) return

        _stateFlow.value = _stateFlow.value.copy(state = TimerState.RUNNING)

        // Start Foreground Service
        startService(context, TimerService.ACTION_SYNC)

        timerJob?.cancel()
        timerJob = scope.launch {
            while (_stateFlow.value.state == TimerState.RUNNING) {
                delay(1000L)
                tick(context)
            }
        }

        PomodoroWidgetProvider.updateAllWidgets(context)
    }

    fun pause(context: Context) {
        timerJob?.cancel()
        timerJob = null
        _stateFlow.value = _stateFlow.value.copy(state = TimerState.PAUSED)
        PomodoroWidgetProvider.updateAllWidgets(context)
        startService(context, TimerService.ACTION_UPDATE_NOTIFICATION)
    }

    fun reset(context: Context) {
        init(context)
        pause(context)
        val repo = getRepo(context)
        val cfg = repo.loadConfig()
        val dur = getDurationForMode(cfg, _stateFlow.value.mode)

        _stateFlow.value = _stateFlow.value.copy(
            state = TimerState.STOPPED,
            totalSeconds = dur,
            remainingSeconds = dur,
            stopwatchSeconds = 0
        )

        PomodoroWidgetProvider.updateAllWidgets(context)
        stopService(context)
    }

    fun switchMode(context: Context, newMode: TimerMode) {
        init(context)
        pause(context)
        val repo = getRepo(context)
        val cfg = repo.loadConfig()
        val dur = getDurationForMode(cfg, newMode)

        _stateFlow.value = _stateFlow.value.copy(
            mode = newMode,
            state = TimerState.STOPPED,
            totalSeconds = dur,
            remainingSeconds = dur,
            stopwatchSeconds = 0
        )

        PomodoroWidgetProvider.updateAllWidgets(context)
    }

    fun setTestPreset(context: Context, minutes: Int) {
        init(context)
        pause(context)
        val sec = minutes * 60

        _stateFlow.value = _stateFlow.value.copy(
            mode = TimerMode.TEST,
            state = TimerState.STOPPED,
            totalSeconds = sec,
            remainingSeconds = sec
        )

        PomodoroWidgetProvider.updateAllWidgets(context)
    }

    fun skipNext(context: Context) {
        init(context)
        handleTimerCompletion(context)
    }

    private fun tick(context: Context) {
        val current = _stateFlow.value
        if (current.mode == TimerMode.STOPWATCH) {
            val nextSec = current.stopwatchSeconds + 1
            _stateFlow.value = current.copy(stopwatchSeconds = nextSec)
            if (nextSec % 60 == 0) {
                val repo = getRepo(context)
                val cfg = repo.loadConfig()
                repo.recordCompletedSession(TimerMode.STOPWATCH, cfg.selectedSubjectId, 1)
            }
            PomodoroWidgetProvider.updateAllWidgets(context)
            startService(context, TimerService.ACTION_UPDATE_NOTIFICATION)
        } else {
            if (current.remainingSeconds > 1) {
                val nextRem = current.remainingSeconds - 1
                _stateFlow.value = current.copy(remainingSeconds = nextRem)
                PomodoroWidgetProvider.updateAllWidgets(context)
                startService(context, TimerService.ACTION_UPDATE_NOTIFICATION)
            } else {
                _stateFlow.value = current.copy(remainingSeconds = 0)
                handleTimerCompletion(context)
            }
        }
    }

    private fun handleTimerCompletion(context: Context) {
        init(context)
        val current = _stateFlow.value
        val repo = getRepo(context)
        val cfg = repo.loadConfig()
        val sound = getSound(context)

        val wasFocus = current.mode == TimerMode.POMODORO || current.mode == TimerMode.TEST

        if (wasFocus) {
            sound.playFocusComplete(cfg.soundEnabled, cfg.vibrateEnabled)
            val durMins = current.totalSeconds / 60
            repo.recordCompletedSession(current.mode, cfg.selectedSubjectId, durMins)

            val newSessionCount = current.sessionCount + 1
            val isLong = newSessionCount % cfg.longBreakInterval == 0
            val nextMode = if (isLong) TimerMode.LONG_BREAK else TimerMode.SHORT_BREAK
            val nextDur = getDurationForMode(cfg, nextMode)

            _stateFlow.value = current.copy(
                sessionCount = newSessionCount,
                mode = nextMode,
                state = if (cfg.autoStartBreaks) TimerState.RUNNING else TimerState.STOPPED,
                totalSeconds = nextDur,
                remainingSeconds = nextDur
            )

            if (cfg.autoStartBreaks) {
                start(context)
            } else {
                pause(context)
                stopService(context)
            }
        } else {
            // Break ended
            sound.playBreakComplete(cfg.soundEnabled, cfg.vibrateEnabled)
            val focusDur = getDurationForMode(cfg, TimerMode.POMODORO)

            _stateFlow.value = current.copy(
                mode = TimerMode.POMODORO,
                state = if (cfg.autoStartPomodoros) TimerState.RUNNING else TimerState.STOPPED,
                totalSeconds = focusDur,
                remainingSeconds = focusDur
            )

            if (cfg.autoStartPomodoros) {
                start(context)
            } else {
                pause(context)
                stopService(context)
            }
        }

        PomodoroWidgetProvider.updateAllWidgets(context)
    }

    private fun startService(context: Context, action: String) {
        try {
            val intent = Intent(context, TimerService::class.java).apply {
                this.action = action
            }
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
        } catch (_: Exception) {}
    }

    private fun stopService(context: Context) {
        try {
            context.stopService(Intent(context, TimerService::class.java))
        } catch (_: Exception) {}
    }
}
