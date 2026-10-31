package com.github.erdogan.pomodorofocuspro.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.github.erdogan.pomodorofocuspro.model.TimerMode

@Composable
fun ModeSelectorTabs(
    activeMode: TimerMode,
    onSelectMode: (TimerMode) -> Unit,
    onSelectTestPreset: (Int) -> Unit,
    modifier: Modifier = Modifier
) {
    val modes = listOf(
        TimerMode.POMODORO,
        TimerMode.SHORT_BREAK,
        TimerMode.LONG_BREAK,
        TimerMode.TEST,
        TimerMode.STOPWATCH
    )

    Column(
        modifier = modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Mode Tabs
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .horizontalScroll(rememberScrollState())
                .padding(horizontal = 16.dp),
            horizontalArrangement = Arrangement.Center
        ) {
            modes.forEach { mode ->
                val isSelected = mode == activeMode
                val accent = mode.getColor()

                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier
                        .padding(horizontal = 4.dp)
                        .clip(RoundedCornerShape(20.dp))
                        .background(
                            if (isSelected) accent else Color(0xFF1E212D)
                        )
                        .clickable { onSelectMode(mode) }
                        .padding(horizontal = 14.dp, vertical = 8.dp)
                ) {
                    Text(text = mode.icon, fontSize = 14.sp)
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = mode.title,
                        color = if (isSelected) Color.White else Color(0xFFADB5BD),
                        fontSize = 13.sp,
                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium
                    )
                }
            }
        }

        // Test Presets (If Test mode is active)
        if (activeMode == TimerMode.TEST) {
            Spacer(modifier = Modifier.height(10.dp))
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 24.dp),
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Süre Seçimi:",
                    color = Color(0xFF9E9E9E),
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Medium
                )
                Spacer(modifier = Modifier.width(8.dp))
                listOf(20, 30, 40).forEach { mins ->
                    Box(
                        modifier = Modifier
                            .padding(horizontal = 4.dp)
                            .clip(RoundedCornerShape(12.dp))
                            .background(Color(0xFF2A2D3A))
                            .clickable { onSelectTestPreset(mins) }
                            .padding(horizontal = 10.dp, vertical = 4.dp)
                    ) {
                        Text(
                            text = "$mins dk",
                            color = Color(0xFFF59E0B),
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }
        }
    }
}
