package com.github.erdogan.pomodorofocuspro.ui.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Pause
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.SkipNext
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.github.erdogan.pomodorofocuspro.model.TimerMode
import com.github.erdogan.pomodorofocuspro.model.TimerState

@Composable
fun ControlsRow(
    state: TimerState,
    mode: TimerMode,
    onStartPause: () -> Unit,
    onReset: () -> Unit,
    onSkipNext: () -> Unit,
    modifier: Modifier = Modifier
) {
    val accentColor = mode.getColor()
    val isRunning = state == TimerState.RUNNING

    val buttonColor by animateColorAsState(
        targetValue = if (isRunning) Color(0xFFE53935) else accentColor,
        label = "btnColor"
    )

    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 24.dp),
        horizontalArrangement = Arrangement.SpaceEvenly,
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Reset Button
        Row(
            modifier = Modifier
                .clip(RoundedCornerShape(24.dp))
                .background(Color(0xFF20232E))
                .clickable { onReset() }
                .padding(horizontal = 16.dp, vertical = 12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = Icons.Default.Refresh,
                contentDescription = "Sıfırla",
                tint = Color(0xFFADB5BD),
                modifier = Modifier.size(18.dp)
            )
            Spacer(modifier = Modifier.width(6.dp))
            Text(
                text = "Sıfırla",
                color = Color(0xFFADB5BD),
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium
            )
        }

        // Play / Pause Main Button
        Row(
            modifier = Modifier
                .shadow(elevation = 8.dp, shape = RoundedCornerShape(28.dp), ambientColor = buttonColor, spotColor = buttonColor)
                .clip(RoundedCornerShape(28.dp))
                .background(buttonColor)
                .clickable { onStartPause() }
                .padding(horizontal = 28.dp, vertical = 14.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = if (isRunning) Icons.Default.Pause else Icons.Default.PlayArrow,
                contentDescription = if (isRunning) "Duraklat" else "Başlat",
                tint = Color.White,
                modifier = Modifier.size(24.dp)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = if (isRunning) "Duraklat" else "Başlat",
                color = Color.White,
                fontSize = 17.sp,
                fontWeight = FontWeight.Bold
            )
        }

        // Skip Next Button
        Row(
            modifier = Modifier
                .clip(RoundedCornerShape(24.dp))
                .background(Color(0xFF20232E))
                .clickable { onSkipNext() }
                .padding(horizontal = 16.dp, vertical = 12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = Icons.Default.SkipNext,
                contentDescription = "Sonraki",
                tint = Color(0xFFADB5BD),
                modifier = Modifier.size(18.dp)
            )
            Spacer(modifier = Modifier.width(6.dp))
            Text(
                text = "Sonraki",
                color = Color(0xFFADB5BD),
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium
            )
        }
    }
}
