package com.github.erdogan.pomodorofocuspro.ui.tabs

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.VisibilityOff
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.github.erdogan.pomodorofocuspro.model.Subject
import com.github.erdogan.pomodorofocuspro.model.WorkspaceProfile
import com.github.erdogan.pomodorofocuspro.ui.main.MainUiState

@Composable
fun WorkspacesTab(
    state: MainUiState,
    onSelectProfile: (String) -> Unit,
    onToggleSubjectVisibility: (String, String) -> Unit,
    onDeleteSubject: (String, String) -> Unit,
    onAddSubjectClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val scrollState = rememberScrollState()
    val profiles = state.config.profiles.values.toList()
    val activeProfileId = state.config.activeProfileId

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(scrollState)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Section: Çalışma Profilleri
        Text(
            text = "🎯 Çalışma Profili Seçimi",
            color = Color.White,
            fontWeight = FontWeight.Bold,
            fontSize = 17.sp
        )

        profiles.forEach { profile ->
            val isActive = profile.id == activeProfileId
            ProfileCard(
                profile = profile,
                isActive = isActive,
                onSelect = { onSelectProfile(profile.id) }
            )
        }

        Spacer(modifier = Modifier.height(8.dp))

        // Section: Dersler & Konular
        val activeProfile = state.activeProfile
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "📚 ${activeProfile?.name ?: "Dersler"}",
                color = Color.White,
                fontWeight = FontWeight.Bold,
                fontSize = 16.sp
            )

            Button(
                onClick = onAddSubjectClick,
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFF10B981),
                    contentColor = Color.White
                ),
                shape = RoundedCornerShape(10.dp),
                contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.Add,
                    contentDescription = "Ders Ekle",
                    modifier = Modifier.size(16.dp)
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text("Ders Ekle", fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
            }
        }

        // Subject Items
        activeProfile?.subjects?.forEach { subject ->
            SubjectListItem(
                subject = subject,
                profileId = activeProfile.id,
                onToggleVisibility = { onToggleSubjectVisibility(activeProfile.id, subject.id) },
                onDelete = { onDeleteSubject(activeProfile.id, subject.id) }
            )
        }

        Spacer(modifier = Modifier.height(16.dp))
    }
}

@Composable
fun ProfileCard(
    profile: WorkspaceProfile,
    isActive: Boolean,
    onSelect: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp))
            .clickable { onSelect() }
            .border(
                width = if (isActive) 2.dp else 1.dp,
                color = if (isActive) Color(0xFF10B981) else Color(0xFF2E384D),
                shape = RoundedCornerShape(16.dp)
            ),
        colors = CardDefaults.cardColors(
            containerColor = if (isActive) Color(0xFF162A29) else Color(0xFF1E222B)
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = profile.name,
                    color = Color.White,
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp
                )

                if (isActive) {
                    Surface(
                        color = Color(0xFF10B981).copy(alpha = 0.2f),
                        shape = RoundedCornerShape(20.dp)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            horizontalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.CheckCircle,
                                contentDescription = "Aktif",
                                tint = Color(0xFF10B981),
                                modifier = Modifier.size(14.dp)
                            )
                            Text(
                                text = "Aktif",
                                color = Color(0xFF10B981),
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                }
            }

            Text(
                text = profile.description,
                color = Color(0xFF94A3B8),
                fontSize = 13.sp
            )

            // Preset Chips
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Surface(
                    color = Color(0x33FFFFFF),
                    shape = RoundedCornerShape(6.dp)
                ) {
                    Text(
                        text = "⏱️ ${profile.defaultFocus} dk Odak",
                        color = Color(0xFFE2E8F0),
                        fontSize = 11.sp,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }

                Surface(
                    color = Color(0x33FFFFFF),
                    shape = RoundedCornerShape(6.dp)
                ) {
                    Text(
                        text = "☕ ${profile.defaultShortBreak} dk Mola",
                        color = Color(0xFFE2E8F0),
                        fontSize = 11.sp,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }

                Surface(
                    color = Color(0x33FFFFFF),
                    shape = RoundedCornerShape(6.dp)
                ) {
                    Text(
                        text = "🎯 ${profile.defaultDailyGoal} Hedef",
                        color = Color(0xFFE2E8F0),
                        fontSize = 11.sp,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }
            }
        }
    }
}

@Composable
fun SubjectListItem(
    subject: Subject,
    profileId: String,
    onToggleVisibility: () -> Unit,
    onDelete: () -> Unit,
    modifier: Modifier = Modifier
) {
    val subColor = subject.parseColor()

    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF1E222B))
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                // Color Pill
                Box(
                    modifier = Modifier
                        .size(10.dp, 28.dp)
                        .clip(RoundedCornerShape(3.dp))
                        .background(subColor)
                )

                Text(text = subject.icon, fontSize = 20.sp)

                Column {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        Text(
                            text = subject.name,
                            color = if (subject.visible) Color.White else Color(0xFF64748B),
                            fontWeight = FontWeight.SemiBold,
                            fontSize = 14.sp
                        )

                        Surface(
                            color = subColor.copy(alpha = 0.2f),
                            shape = RoundedCornerShape(4.dp)
                        ) {
                            Text(
                                text = subject.badge,
                                color = subColor,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.padding(horizontal = 4.dp, vertical = 1.dp)
                            )
                        }
                    }
                }
            }

            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                // Visibility Toggle
                IconButton(
                    onClick = onToggleVisibility,
                    modifier = Modifier.size(36.dp)
                ) {
                    Icon(
                        imageVector = if (subject.visible) Icons.Default.Visibility else Icons.Default.VisibilityOff,
                        contentDescription = "Görünürlük",
                        tint = if (subject.visible) Color(0xFF10B981) else Color(0xFF64748B),
                        modifier = Modifier.size(18.dp)
                    )
                }

                // Delete Button
                IconButton(
                    onClick = onDelete,
                    modifier = Modifier.size(36.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Delete,
                        contentDescription = "Sil",
                        tint = Color(0xFFEF4444),
                        modifier = Modifier.size(18.dp)
                    )
                }
            }
        }
    }
}
