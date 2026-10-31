package com.github.erdogan.pomodorofocuspro.ui.components

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.github.erdogan.pomodorofocuspro.model.Subject
import com.github.erdogan.pomodorofocuspro.model.TimerMode

@Composable
fun CircularTimerRing(
    progressRatio: Float,
    formattedTime: String,
    mode: TimerMode,
    activeSubject: Subject?,
    sessionCount: Int,
    longBreakInterval: Int,
    modifier: Modifier = Modifier
) {
    val animatedProgress by animateFloatAsState(
        targetValue = progressRatio,
        animationSpec = tween(durationMillis = 350),
        label = "progress"
    )

    val accentColor = mode.getColor()
    val trackColor = Color(0xFF1E212D)

    Box(
        modifier = modifier
            .size(280.dp)
            .padding(8.dp),
        contentAlignment = Alignment.Center
    ) {
        // Outer glow & canvas
        Canvas(modifier = Modifier.fillMaxSize()) {
            val strokeWidth = 14.dp.toPx()

            // Background circle track
            drawCircle(
                color = trackColor,
                style = Stroke(width = strokeWidth)
            )

            // Progress arc
            if (animatedProgress > 0.001f) {
                drawArc(
                    brush = Brush.sweepGradient(
                        colors = listOf(
                            accentColor.copy(alpha = 0.7f),
                            accentColor,
                            accentColor
                        )
                    ),
                    startAngle = -90f,
                    sweepAngle = 360f * animatedProgress,
                    useCenter = false,
                    style = Stroke(width = strokeWidth, cap = StrokeCap.Round)
                )
            }
        }

        // Inside content
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // Big digital clock
            Text(
                text = formattedTime,
                fontSize = 54.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White,
                letterSpacing = 1.sp
            )

            Spacer(modifier = Modifier.height(6.dp))

            // Active Subject Chip Badge
            if (activeSubject != null && (mode == TimerMode.POMODORO || mode == TimerMode.TEST)) {
                val subColor = activeSubject.parseColor()
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier
                        .clip(RoundedCornerShape(12.dp))
                        .background(subColor.copy(alpha = 0.2f))
                        .padding(horizontal = 12.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = activeSubject.icon,
                        fontSize = 14.sp
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = activeSubject.name.uppercase(),
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        color = subColor
                    )
                }
            } else {
                Text(
                    text = mode.title.uppercase(),
                    fontSize = 13.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = accentColor
                )
            }

            Spacer(modifier = Modifier.height(10.dp))

            // Cycle dots (e.g. 4 dots: ● ○ ○ ○)
            if (mode == TimerMode.POMODORO || mode == TimerMode.SHORT_BREAK || mode == TimerMode.LONG_BREAK) {
                val cyclePos = sessionCount % longBreakInterval
                Row(
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    for (i in 0 until longBreakInterval) {
                        val isFilled = i < cyclePos
                        Box(
                            modifier = Modifier
                                .size(7.dp)
                                .clip(CircleShape)
                                .background(
                                    if (isFilled) accentColor else Color(0xFF454B5C)
                                )
                        )
                    }
                }
            }
        }
    }
}
