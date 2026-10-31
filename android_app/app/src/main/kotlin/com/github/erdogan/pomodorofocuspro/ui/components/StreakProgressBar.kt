package com.github.erdogan.pomodorofocuspro.ui.components

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun StreakProgressBar(
    completedSessions: Int,
    dailyGoal: Int,
    currentStreak: Int,
    modifier: Modifier = Modifier
) {
    val remaining = (dailyGoal - completedSessions).coerceAtLeast(0)
    val ratio = if (dailyGoal > 0) (completedSessions.toFloat() / dailyGoal.toFloat()).coerceIn(0f, 1f) else 0f

    val animatedRatio by animateFloatAsState(
        targetValue = ratio,
        animationSpec = tween(durationMillis = 400),
        label = "streakProgress"
    )

    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp, vertical = 6.dp)
            .clip(RoundedCornerShape(16.dp))
            .background(Color(0xFF1E212D))
            .padding(horizontal = 14.dp, vertical = 10.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = if (remaining > 0) {
                    "🎯 Günlük Hedef: $completedSessions/$dailyGoal Seans • Zincire $remaining Kaldı!"
                } else {
                    "🎉 Tebrikler! Bugünün Hedefi Tamamlandı ($completedSessions/$dailyGoal)"
                },
                color = Color(0xFFE2E8F0),
                fontSize = 12.sp,
                fontWeight = FontWeight.SemiBold
            )

            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = "🔥 Zincir: $currentStreak Gün",
                    color = Color(0xFFF59E0B),
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }

        Spacer(modifier = Modifier.height(8.dp))

        // Progress track
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(7.dp)
                .clip(RoundedCornerShape(4.dp))
                .background(Color(0xFF2C3040))
        ) {
            if (animatedRatio > 0.001f) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth(animatedRatio)
                        .fillMaxHeight()
                        .clip(RoundedCornerShape(4.dp))
                        .background(
                            Brush.horizontalGradient(
                                colors = listOf(Color(0xFFFF5252), Color(0xFFF59E0B))
                            )
                        )
                )
            }
        }
    }
}
