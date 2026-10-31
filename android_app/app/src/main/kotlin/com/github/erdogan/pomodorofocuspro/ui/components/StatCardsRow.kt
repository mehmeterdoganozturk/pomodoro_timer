package com.github.erdogan.pomodorofocuspro.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
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

@Composable
fun StatCardsRow(
    completedSessions: Int,
    dailyGoal: Int,
    focusMinutes: Int,
    breakCount: Int,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp, vertical = 6.dp),
        horizontalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        // Card 1: Seanslar
        StatCard(
            icon = "🍅",
            title = "SEANSLAR",
            value = "$completedSessions",
            subtitle = "Hedef: $dailyGoal",
            color = Color(0xFFFF5252),
            modifier = Modifier.weight(1f)
        )

        // Card 2: Odaklanma
        StatCard(
            icon = "⏱️",
            title = "ODAKLANMA",
            value = if (focusMinutes >= 60) "${focusMinutes / 60}s ${focusMinutes % 60}dk" else "$focusMinutes dk",
            subtitle = "Bugün",
            color = Color(0xFF06B6D4),
            modifier = Modifier.weight(1f)
        )

        // Card 3: Molalar
        StatCard(
            icon = "☕",
            title = "MOLALAR",
            value = "$breakCount",
            subtitle = "Bugün",
            color = Color(0xFF10B981),
            modifier = Modifier.weight(1f)
        )
    }
}

@Composable
fun StatCard(
    icon: String,
    title: String,
    value: String,
    subtitle: String,
    color: Color,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .clip(RoundedCornerShape(16.dp))
            .background(Color(0xFF1E212D))
            .padding(12.dp)
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(text = icon, fontSize = 13.sp)
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text = title,
                color = Color(0xFF94A3B8),
                fontSize = 10.sp,
                fontWeight = FontWeight.Bold
            )
        }

        Spacer(modifier = Modifier.height(6.dp))

        Text(
            text = value,
            color = Color.White,
            fontSize = 18.sp,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(2.dp))

        Text(
            text = subtitle,
            color = Color(0xFF64748B),
            fontSize = 11.sp
        )
    }
}
