package com.github.erdogan.pomodorofocuspro.ui.main

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.github.erdogan.pomodorofocuspro.ui.components.AddSubjectDialog
import com.github.erdogan.pomodorofocuspro.ui.components.SettingsDialog
import com.github.erdogan.pomodorofocuspro.ui.tabs.StreakTab
import com.github.erdogan.pomodorofocuspro.ui.tabs.TimerTab
import com.github.erdogan.pomodorofocuspro.ui.tabs.WorkspacesTab

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(
    modifier: Modifier = Modifier,
    viewModel: MainScreenViewModel = viewModel()
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()

    Scaffold(
        modifier = modifier.fillMaxSize(),
        containerColor = Color(0xFF0F1117),
        topBar = {
            TopAppBar(
                title = {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = "🍅",
                            fontSize = 22.sp
                        )
                        Text(
                            text = "Pomodoro Pro",
                            fontWeight = FontWeight.Bold,
                            fontSize = 18.sp,
                            color = Color.White
                        )
                    }
                },
                actions = {
                    IconButton(
                        onClick = { viewModel.setSettingsOpen(true) },
                        modifier = Modifier.padding(end = 4.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Settings,
                            contentDescription = "Ayarlar",
                            tint = Color(0xFF94A3B8)
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Color(0xFF141721),
                    titleContentColor = Color.White
                )
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            // Segmented Tab Selector
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 10.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(Color(0xFF1B1F2A))
                    .padding(4.dp),
                horizontalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                val tabs = listOf(
                    Triple(0, "⏱️", "Sayaç"),
                    Triple(1, "🔥", "Zinciri Kırma"),
                    Triple(2, "🎯", "Modlar")
                )

                tabs.forEach { (index, icon, title) ->
                    val isSelected = state.selectedTab == index
                    Box(
                        modifier = Modifier
                            .weight(1f)
                            .clip(RoundedCornerShape(8.dp))
                            .background(if (isSelected) Color(0xFF2E384D) else Color.Transparent)
                            .clickable { viewModel.selectTab(index) }
                            .padding(vertical = 8.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            Text(text = icon, fontSize = 13.sp)
                            Text(
                                text = title,
                                color = if (isSelected) Color.White else Color(0xFF94A3B8),
                                fontSize = 12.sp,
                                fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium
                            )
                        }
                    }
                }
            }

            // Tab Content
            Box(modifier = Modifier.fillMaxSize()) {
                when (state.selectedTab) {
                    0 -> TimerTab(
                        state = state,
                        onSelectMode = { viewModel.switchMode(it) },
                        onSelectTestPreset = { viewModel.setTestPreset(it) },
                        onSelectSubject = { viewModel.selectSubject(it) },
                        onAddSubjectClick = { viewModel.setAddSubjectOpen(true) },
                        onStartPause = { viewModel.toggleStartPause() },
                        onReset = { viewModel.reset() },
                        onSkipNext = { viewModel.skipNext() }
                    )
                    1 -> StreakTab(
                        state = state
                    )
                    2 -> WorkspacesTab(
                        state = state,
                        onSelectProfile = { viewModel.selectProfile(it) },
                        onToggleSubjectVisibility = { profId, subId ->
                            viewModel.toggleSubjectVisibility(profId, subId)
                        },
                        onDeleteSubject = { profId, subId ->
                            viewModel.deleteSubject(profId, subId)
                        },
                        onAddSubjectClick = { viewModel.setAddSubjectOpen(true) }
                    )
                }
            }
        }
    }

    // Modal Settings Dialog
    if (state.isSettingsOpen) {
        SettingsDialog(
            config = state.config,
            onDismiss = { viewModel.setSettingsOpen(false) },
            onSave = { focus, test, shortBreak, longBreak, interval, goal, sound, vib, autoB, autoP ->
                viewModel.saveSettings(
                    focusDur = focus,
                    testDur = test,
                    shortDur = shortBreak,
                    longDur = longBreak,
                    longInterval = interval,
                    goal = goal,
                    sound = sound,
                    vibrate = vib,
                    autoBreaks = autoB,
                    autoPomodoros = autoP
                )
            }
        )
    }

    // Modal Add Subject Dialog
    if (state.isAddSubjectOpen) {
        val activeProfileName = state.activeProfile?.name ?: "Aktif Profil"
        AddSubjectDialog(
            profileName = activeProfileName,
            onDismiss = { viewModel.setAddSubjectOpen(false) },
            onConfirm = { name, icon, colorHex, badge ->
                viewModel.addSubject(
                    profileId = state.config.activeProfileId,
                    name = name,
                    icon = icon,
                    colorHex = colorHex,
                    badge = badge
                )
            }
        )
    }
}
