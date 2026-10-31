package com.github.erdogan.pomodorofocuspro.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Remove
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import com.github.erdogan.pomodorofocuspro.model.PomodoroConfig

@Composable
fun SettingsDialog(
    config: PomodoroConfig,
    onDismiss: () -> Unit,
    onSave: (
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
    ) -> Unit
) {
    var focusDuration by remember { mutableStateOf(config.focusDuration) }
    var testDuration by remember { mutableStateOf(config.testDuration) }
    var shortBreakDuration by remember { mutableStateOf(config.shortBreakDuration) }
    var longBreakDuration by remember { mutableStateOf(config.longBreakDuration) }
    var longBreakInterval by remember { mutableStateOf(config.longBreakInterval) }
    var dailyGoal by remember { mutableStateOf(config.dailyGoal) }
    var soundEnabled by remember { mutableStateOf(config.soundEnabled) }
    var vibrateEnabled by remember { mutableStateOf(config.vibrateEnabled) }
    var autoStartBreaks by remember { mutableStateOf(config.autoStartBreaks) }
    var autoStartPomodoros by remember { mutableStateOf(config.autoStartPomodoros) }

    Dialog(onDismissRequest = onDismiss) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .wrapContentHeight()
                .padding(vertical = 16.dp),
            shape = RoundedCornerShape(24.dp),
            colors = CardDefaults.cardColors(containerColor = Color(0xFF1B1F27))
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(20.dp)
                    .verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Header
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "⚙️ Sayaç Ayarları",
                        color = Color.White,
                        fontWeight = FontWeight.Bold,
                        fontSize = 20.sp
                    )
                }

                HorizontalDivider(color = Color(0xFF2E384D))

                // Section: Süreler
                Text(
                    text = "⏱️ Süreler & Aralıklar",
                    color = Color(0xFF94A3B8),
                    fontSize = 13.sp,
                    fontWeight = FontWeight.SemiBold
                )

                StepperRow(
                    title = "Odaklanma Süresi",
                    valueText = "$focusDuration dk",
                    onMinus = { if (focusDuration > 5) focusDuration -= 5 },
                    onPlus = { if (focusDuration < 120) focusDuration += 5 }
                )

                StepperRow(
                    title = "Test / Sınav Süresi",
                    valueText = "$testDuration dk",
                    onMinus = { if (testDuration > 5) testDuration -= 5 },
                    onPlus = { if (testDuration < 120) testDuration += 5 }
                )

                StepperRow(
                    title = "Kısa Mola",
                    valueText = "$shortBreakDuration dk",
                    onMinus = { if (shortBreakDuration > 1) shortBreakDuration -= 1 },
                    onPlus = { if (shortBreakDuration < 30) shortBreakDuration += 1 }
                )

                StepperRow(
                    title = "Uzun Mola",
                    valueText = "$longBreakDuration dk",
                    onMinus = { if (longBreakDuration > 5) longBreakDuration -= 5 },
                    onPlus = { if (longBreakDuration < 60) longBreakDuration += 5 }
                )

                StepperRow(
                    title = "Uzun Mola Aralığı",
                    valueText = "$longBreakInterval Seans",
                    onMinus = { if (longBreakInterval > 2) longBreakInterval -= 1 },
                    onPlus = { if (longBreakInterval < 12) longBreakInterval += 1 }
                )

                StepperRow(
                    title = "Günlük Hedef",
                    valueText = "$dailyGoal Seans",
                    onMinus = { if (dailyGoal > 1) dailyGoal -= 1 },
                    onPlus = { if (dailyGoal < 30) dailyGoal += 1 }
                )

                HorizontalDivider(color = Color(0xFF2E384D))

                // Section: Otomasyon & Bildirimler
                Text(
                    text = "🔔 Bildirim & Otomasyon",
                    color = Color(0xFF94A3B8),
                    fontSize = 13.sp,
                    fontWeight = FontWeight.SemiBold
                )

                SwitchRow(
                    title = "Sesli Bildirim",
                    subtitle = "Süre bittiğinde tamamlanma sesi çal",
                    checked = soundEnabled,
                    onCheckedChange = { soundEnabled = it }
                )

                SwitchRow(
                    title = "Titreşimli Uyarı",
                    subtitle = "Süre bittiğinde telefonu titret",
                    checked = vibrateEnabled,
                    onCheckedChange = { vibrateEnabled = it }
                )

                SwitchRow(
                    title = "Otomatik Mola Başlat",
                    subtitle = "Odaklanma bitince molaya kendiliğinden geç",
                    checked = autoStartBreaks,
                    onCheckedChange = { autoStartBreaks = it }
                )

                SwitchRow(
                    title = "Otomatik Odaklanma Başlat",
                    subtitle = "Mola bitince yeni odak seansını başlat",
                    checked = autoStartPomodoros,
                    onCheckedChange = { autoStartPomodoros = it }
                )

                Spacer(modifier = Modifier.height(8.dp))

                // Action Buttons
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    OutlinedButton(
                        onClick = onDismiss,
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(12.dp),
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = Color(0xFF94A3B8))
                    ) {
                        Text("Vazgeç")
                    }

                    Button(
                        onClick = {
                            onSave(
                                focusDuration,
                                testDuration,
                                shortBreakDuration,
                                longBreakDuration,
                                longBreakInterval,
                                dailyGoal,
                                soundEnabled,
                                vibrateEnabled,
                                autoStartBreaks,
                                autoStartPomodoros
                            )
                            onDismiss()
                        },
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(12.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFF10B981),
                            contentColor = Color.White
                        )
                    ) {
                        Text("Kaydet", fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}

@Composable
fun StepperRow(
    title: String,
    valueText: String,
    onMinus: () -> Unit,
    onPlus: () -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = title,
            color = Color.White,
            fontSize = 14.sp
        )

        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            FilledIconButton(
                onClick = onMinus,
                modifier = Modifier.size(32.dp),
                shape = RoundedCornerShape(8.dp),
                colors = IconButtonDefaults.filledIconButtonColors(containerColor = Color(0xFF2E384D))
            ) {
                Icon(
                    imageVector = Icons.Default.Remove,
                    contentDescription = "Azalt",
                    tint = Color.White,
                    modifier = Modifier.size(16.dp)
                )
            }

            Text(
                text = valueText,
                color = Color(0xFF10B981),
                fontWeight = FontWeight.Bold,
                fontSize = 14.sp,
                modifier = Modifier.widthIn(min = 52.dp),
                textAlign = androidx.compose.ui.text.style.TextAlign.Center
            )

            FilledIconButton(
                onClick = onPlus,
                modifier = Modifier.size(32.dp),
                shape = RoundedCornerShape(8.dp),
                colors = IconButtonDefaults.filledIconButtonColors(containerColor = Color(0xFF2E384D))
            ) {
                Icon(
                    imageVector = Icons.Default.Add,
                    contentDescription = "Artır",
                    tint = Color.White,
                    modifier = Modifier.size(16.dp)
                )
            }
        }
    }
}

@Composable
fun SwitchRow(
    title: String,
    subtitle: String,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = title,
                color = Color.White,
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium
            )
            Text(
                text = subtitle,
                color = Color(0xFF64748B),
                fontSize = 11.sp
            )
        }

        Switch(
            checked = checked,
            onCheckedChange = onCheckedChange,
            colors = SwitchDefaults.colors(
                checkedThumbColor = Color.White,
                checkedTrackColor = Color(0xFF10B981),
                uncheckedThumbColor = Color(0xFF94A3B8),
                uncheckedTrackColor = Color(0xFF2E384D)
            )
        )
    }
}
