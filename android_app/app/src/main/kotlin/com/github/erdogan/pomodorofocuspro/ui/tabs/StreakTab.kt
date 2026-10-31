package com.github.erdogan.pomodorofocuspro.ui.tabs

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.github.erdogan.pomodorofocuspro.model.DailyRecord
import com.github.erdogan.pomodorofocuspro.ui.main.MainUiState
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Date
import java.util.Locale

@Composable
fun StreakTab(
    state: MainUiState,
    modifier: Modifier = Modifier
) {
    val scrollState = rememberScrollState()

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(scrollState)
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // 1. Fire Banner (Zincir Rozeti)
        StreakFireBanner(
            currentStreak = state.streak,
            bestStreak = state.bestStreak
        )

        // 2. Heatmap Grid (28 Günlük Zincir)
        HeatmapCard(
            heatmapDays = state.heatmapDays,
            dailyGoal = state.config.dailyGoal
        )

        // 3. Today's Subject Breakdown (Ders Dağılımı)
        SubjectBreakdownCard(
            todayRecord = state.todayRecord,
            state = state
        )

        Spacer(modifier = Modifier.height(16.dp))
    }
}

@Composable
fun StreakFireBanner(
    currentStreak: Int,
    bestStreak: Int,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = Color.Transparent)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    brush = Brush.verticalGradient(
                        colors = listOf(
                            Color(0xFFDC2626),
                            Color(0xFFEA580C),
                            Color(0xFF9A3412)
                        )
                    )
                )
                .padding(20.dp),
            contentAlignment = Alignment.Center
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                Text(
                    text = "🔥",
                    fontSize = 44.sp
                )

                Text(
                    text = "$currentStreak GÜNLÜK ZİNCİR",
                    color = Color.White,
                    fontWeight = FontWeight.Black,
                    fontSize = 24.sp,
                    letterSpacing = 1.sp
                )

                Text(
                    text = if (bestStreak > 0) "🏆 En İyi Rekor: $bestStreak Gün" else "İlk zincirini bugün başlat!",
                    color = Color(0xFFFED7AA),
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium
                )

                Spacer(modifier = Modifier.height(6.dp))

                Surface(
                    color = Color(0x33000000),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text(
                        text = "\"Günde 1 saat fazla çalışan bir öğrenci, yılda 365 saat öne geçer!\"",
                        color = Color(0xFFFFF7ED),
                        fontSize = 12.sp,
                        fontStyle = androidx.compose.ui.text.font.FontStyle.Italic,
                        textAlign = TextAlign.Center,
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                    )
                }
            }
        }
    }
}

@Composable
fun HeatmapCard(
    heatmapDays: List<Pair<Date, DailyRecord>>,
    dailyGoal: Int,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(18.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF1E222B))
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "📅 28 Günlük Aktivite",
                    color = Color.White,
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp
                )
                Text(
                    text = "Hedef: $dailyGoal Seans",
                    color = Color(0xFF94A3B8),
                    fontSize = 12.sp
                )
            }

            // 7 Days of the week headers
            val dayHeaders = listOf("Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz")
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                dayHeaders.forEach { header ->
                    Text(
                        text = header,
                        color = Color(0xFF64748B),
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        textAlign = TextAlign.Center,
                        modifier = Modifier.weight(1f)
                    )
                }
            }

            // 28 Days Grid (4 rows of 7 days)
            val dayFormat = SimpleDateFormat("d", Locale.getDefault())
            val rows = heatmapDays.chunked(7)

            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                rows.forEach { rowDays ->
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        rowDays.forEach { (date, record) ->
                            val cellColor = getHeatmapCellColor(record.completedSessions, dailyGoal)
                            val dayNum = dayFormat.format(date)
                            val isGoalMet = record.completedSessions >= dailyGoal

                            Box(
                                modifier = Modifier
                                    .weight(1f)
                                    .aspectRatio(1f)
                                    .clip(RoundedCornerShape(8.dp))
                                    .background(cellColor)
                                    .border(
                                        width = if (isGoalMet) 1.5.dp else 0.5.dp,
                                        color = if (isGoalMet) Color(0xFF34D399) else Color(0x33FFFFFF),
                                        shape = RoundedCornerShape(8.dp)
                                    ),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = dayNum,
                                    color = if (record.completedSessions > 0) Color.White else Color(0xFF94A3B8),
                                    fontSize = 11.sp,
                                    fontWeight = if (isGoalMet) FontWeight.Bold else FontWeight.Normal
                                )
                            }
                        }
                    }
                }
            }

            // Legend
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 4.dp),
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("Az", color = Color(0xFF64748B), fontSize = 11.sp)
                Spacer(modifier = Modifier.width(6.dp))

                listOf(
                    Color(0xFF242B38),
                    Color(0xFF065F46),
                    Color(0xFF059669),
                    Color(0xFF10B981)
                ).forEach { color ->
                    Box(
                        modifier = Modifier
                            .size(14.dp)
                            .clip(RoundedCornerShape(3.dp))
                            .background(color)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                }

                Spacer(modifier = Modifier.width(2.dp))
                Text("Hedef", color = Color(0xFF64748B), fontSize = 11.sp)
            }
        }
    }
}

private fun getHeatmapCellColor(completedSessions: Int, dailyGoal: Int): Color {
    return when {
        completedSessions <= 0 -> Color(0xFF242B38)
        completedSessions < (dailyGoal / 2).coerceAtLeast(2) -> Color(0xFF065F46)
        completedSessions < dailyGoal -> Color(0xFF059669)
        else -> Color(0xFF10B981)
    }
}

@Composable
fun SubjectBreakdownCard(
    todayRecord: DailyRecord,
    state: MainUiState,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(18.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF1E222B))
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "📊 Bugünkü Ders Dağılımı",
                    color = Color.White,
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp
                )
                Text(
                    text = "${todayRecord.focusMinutes} Dk Toplam",
                    color = Color(0xFF10B981),
                    fontWeight = FontWeight.Bold,
                    fontSize = 13.sp
                )
            }

            if (todayRecord.subjectMinutes.isEmpty() || todayRecord.focusMinutes == 0) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 24.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        Text(text = "🎯", fontSize = 28.sp)
                        Text(
                            text = "Henüz bugün tamamlanmış ders kaydı yok.",
                            color = Color(0xFF94A3B8),
                            fontSize = 13.sp
                        )
                        Text(
                            text = "Haydi ilk odaklanma seansını başlat!",
                            color = Color(0xFF64748B),
                            fontSize = 12.sp
                        )
                    }
                }
            } else {
                val allSubjects = state.config.profiles.values
                    .flatMap { it.subjects }
                    .associateBy { it.id }

                val totalMinutes = todayRecord.focusMinutes.coerceAtLeast(1)

                Column(
                    modifier = Modifier.fillMaxWidth(),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    todayRecord.subjectMinutes.forEach { (subId, minutes) ->
                        if (minutes > 0) {
                            val subject = allSubjects[subId]
                            val subName = subject?.name ?: "Bilinmeyen Ders"
                            val subIcon = subject?.icon ?: "📖"
                            val subBadge = subject?.badge ?: "Genel"
                            val subColor = subject?.parseColor() ?: Color(0xFF3B82F6)
                            val ratio = (minutes.toFloat() / totalMinutes.toFloat()).coerceIn(0f, 1f)
                            val percent = (ratio * 100).toInt()

                            Column(
                                modifier = Modifier.fillMaxWidth(),
                                verticalArrangement = Arrangement.spacedBy(4.dp)
                            ) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Row(
                                        verticalAlignment = Alignment.CenterVertically,
                                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                                    ) {
                                        Text(text = subIcon, fontSize = 14.sp)
                                        Text(
                                            text = subName,
                                            color = Color.White,
                                            fontSize = 13.sp,
                                            fontWeight = FontWeight.Medium
                                        )
                                        Surface(
                                            color = subColor.copy(alpha = 0.2f),
                                            shape = RoundedCornerShape(4.dp)
                                        ) {
                                            Text(
                                                text = subBadge,
                                                color = subColor,
                                                fontSize = 10.sp,
                                                fontWeight = FontWeight.Bold,
                                                modifier = Modifier.padding(horizontal = 4.dp, vertical = 1.dp)
                                            )
                                        }
                                    }

                                    Text(
                                        text = "$minutes dk (%$percent)",
                                        color = Color(0xFF94A3B8),
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.Medium
                                    )
                                }

                                // Linear Progress Bar
                                Box(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .height(8.dp)
                                        .clip(RoundedCornerShape(4.dp))
                                        .background(Color(0xFF262E3D))
                                ) {
                                    Box(
                                        modifier = Modifier
                                            .fillMaxWidth(ratio)
                                            .fillMaxHeight()
                                            .clip(RoundedCornerShape(4.dp))
                                            .background(subColor)
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
