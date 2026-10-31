package com.github.erdogan.pomodorofocuspro.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog

@Composable
fun AddSubjectDialog(
    profileName: String,
    onDismiss: () -> Unit,
    onConfirm: (name: String, icon: String, colorHex: String, badge: String) -> Unit
) {
    var name by remember { mutableStateOf("") }
    var selectedIcon by remember { mutableStateOf("📖") }
    var badge by remember { mutableStateOf("Genel") }
    var selectedColorHex by remember { mutableStateOf("#3B82F6") }

    val presetIcons = listOf("📖", "📐", "🔬", "🧪", "💻", "⚡", "🏗️", "🎯", "📊", "📝", "🎨", "🌐")
    val presetBadges = listOf("Genel", "TYT", "AYT", "Dev", "Sınav", "Proje")
    val presetColors = listOf(
        "#3B82F6", // Blue
        "#10B981", // Emerald
        "#F59E0B", // Amber
        "#EF4444", // Red
        "#8B5CF6", // Purple
        "#EC4899", // Pink
        "#06B6D4", // Cyan
        "#84CC16"  // Lime
    )

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
                Text(
                    text = "➕ Yeni Ders Ekle",
                    color = Color.White,
                    fontWeight = FontWeight.Bold,
                    fontSize = 18.sp
                )
                Text(
                    text = "$profileName profiline eklenecek",
                    color = Color(0xFF94A3B8),
                    fontSize = 12.sp
                )

                HorizontalDivider(color = Color(0xFF2E384D))

                // Ders Adı
                OutlinedTextField(
                    value = name,
                    onValueChange = { name = it },
                    label = { Text("Ders / Konu Adı") },
                    placeholder = { Text("Örn: Organik Kimya") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth(),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = Color.White,
                        unfocusedTextColor = Color.White,
                        focusedBorderColor = Color(0xFF10B981),
                        unfocusedBorderColor = Color(0xFF2E384D),
                        focusedLabelColor = Color(0xFF10B981),
                        unfocusedLabelColor = Color(0xFF94A3B8)
                    )
                )

                // İkon Seçimi
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(
                        text = "İkon Seçimi",
                        color = Color(0xFF94A3B8),
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        presetIcons.take(6).forEach { icon ->
                            IconSelectChip(
                                icon = icon,
                                isSelected = selectedIcon == icon,
                                onClick = { selectedIcon = icon }
                            )
                        }
                    }

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        presetIcons.drop(6).forEach { icon ->
                            IconSelectChip(
                                icon = icon,
                                isSelected = selectedIcon == icon,
                                onClick = { selectedIcon = icon }
                            )
                        }
                    }
                }

                // Rozet / Etiket Seçimi
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(
                        text = "Etiket / Rozet",
                        color = Color(0xFF94A3B8),
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        presetBadges.forEach { b ->
                            val isSel = badge == b
                            Surface(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(8.dp))
                                    .clickable { badge = b },
                                color = if (isSel) Color(0xFF10B981) else Color(0xFF242B38),
                                shape = RoundedCornerShape(8.dp)
                            ) {
                                Text(
                                    text = b,
                                    color = if (isSel) Color.White else Color(0xFF94A3B8),
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold,
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 5.dp)
                                )
                            }
                        }
                    }
                }

                // Renk Seçimi
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(
                        text = "Renk",
                        color = Color(0xFF94A3B8),
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        presetColors.forEach { hex ->
                            val color = try {
                                Color(hex.removePrefix("#").toLong(16) or 0xFF000000)
                            } catch (_: Exception) {
                                Color(0xFF3B82F6)
                            }
                            val isSel = selectedColorHex == hex

                            Box(
                                modifier = Modifier
                                    .size(28.dp)
                                    .clip(CircleShape)
                                    .background(color)
                                    .clickable { selectedColorHex = hex }
                                    .border(
                                        width = if (isSel) 2.5.dp else 0.dp,
                                        color = if (isSel) Color.White else Color.Transparent,
                                        shape = CircleShape
                                    )
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(6.dp))

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
                            if (name.isNotBlank()) {
                                onConfirm(name.trim(), selectedIcon, selectedColorHex, badge)
                                onDismiss()
                            }
                        },
                        enabled = name.isNotBlank(),
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(12.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFF10B981),
                            contentColor = Color.White
                        )
                    ) {
                        Text("Ekle", fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}

@Composable
fun IconSelectChip(
    icon: String,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Box(
        modifier = Modifier
            .size(38.dp)
            .clip(RoundedCornerShape(8.dp))
            .background(if (isSelected) Color(0xFF10B981).copy(alpha = 0.3f) else Color(0xFF242B38))
            .border(
                width = if (isSelected) 1.5.dp else 0.dp,
                color = if (isSelected) Color(0xFF10B981) else Color.Transparent,
                shape = RoundedCornerShape(8.dp)
            )
            .clickable { onClick() },
        contentAlignment = Alignment.Center
    ) {
        Text(text = icon, fontSize = 18.sp)
    }
}
