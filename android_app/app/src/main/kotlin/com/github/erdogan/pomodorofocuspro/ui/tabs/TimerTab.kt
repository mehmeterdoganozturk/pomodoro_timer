package com.github.erdogan.pomodorofocuspro.ui.tabs

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.github.erdogan.pomodorofocuspro.ui.components.*
import com.github.erdogan.pomodorofocuspro.ui.main.MainUiState

@Composable
fun TimerTab(
    state: MainUiState,
    onSelectMode: (com.github.erdogan.pomodorofocuspro.model.TimerMode) -> Unit,
    onSelectTestPreset: (Int) -> Unit,
    onSelectSubject: (String) -> Unit,
    onAddSubjectClick: () -> Unit,
    onStartPause: () -> Unit,
    onReset: () -> Unit,
    onSkipNext: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        Spacer(modifier = Modifier.height(4.dp))

        // Mode Tabs
        ModeSelectorTabs(
            activeMode = state.mode,
            onSelectMode = onSelectMode,
            onSelectTestPreset = onSelectTestPreset
        )

        // Subject Chips Row (Only visible for Pomodoro, Test, Stopwatch)
        if (state.mode != com.github.erdogan.pomodorofocuspro.model.TimerMode.SHORT_BREAK &&
            state.mode != com.github.erdogan.pomodorofocuspro.model.TimerMode.LONG_BREAK
        ) {
            val subjects = state.activeProfile?.subjects ?: emptyList()
            SubjectChipRow(
                subjects = subjects,
                selectedSubjectId = state.config.selectedSubjectId,
                onSelectSubject = onSelectSubject,
                onAddSubjectClick = onAddSubjectClick
            )
        }

        // Circular Timer Ring
        CircularTimerRing(
            progressRatio = state.progressRatio,
            formattedTime = state.formattedTime,
            mode = state.mode,
            activeSubject = state.activeSubject,
            sessionCount = state.sessionCount,
            longBreakInterval = state.config.longBreakInterval,
            modifier = Modifier.padding(vertical = 4.dp)
        )

        // Streak Progress Bar
        StreakProgressBar(
            completedSessions = state.todayRecord.completedSessions,
            dailyGoal = state.config.dailyGoal,
            currentStreak = state.streak
        )

        // Control Buttons (Start / Pause / Reset / Skip)
        ControlsRow(
            state = state.state,
            mode = state.mode,
            onStartPause = onStartPause,
            onReset = onReset,
            onSkipNext = onSkipNext
        )

        // Bottom Stats
        StatCardsRow(
            completedSessions = state.todayRecord.completedSessions,
            dailyGoal = state.config.dailyGoal,
            focusMinutes = state.todayRecord.focusMinutes,
            breakCount = state.todayRecord.breakCount
        )

        Spacer(modifier = Modifier.height(16.dp))
    }
}
