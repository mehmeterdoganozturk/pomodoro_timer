package com.github.erdogan.pomodorofocuspro.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.github.erdogan.pomodorofocuspro.model.Subject

@Composable
fun SubjectChipRow(
    subjects: List<Subject>,
    selectedSubjectId: String,
    onSelectSubject: (String) -> Unit,
    onAddSubjectClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val visibleSubjects = subjects.filter { it.visible }

    Row(
        modifier = modifier
            .fillMaxWidth()
            .horizontalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        visibleSubjects.forEach { sub ->
            val isSelected = sub.id == selectedSubjectId
            val subColor = sub.parseColor()

            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier
                    .padding(end = 8.dp)
                    .clip(RoundedCornerShape(16.dp))
                    .background(
                        if (isSelected) subColor.copy(alpha = 0.25f) else Color(0xFF1E212D)
                    )
                    .border(
                        width = if (isSelected) 1.5.dp else 0.dp,
                        color = if (isSelected) subColor else Color.Transparent,
                        shape = RoundedCornerShape(16.dp)
                    )
                    .clickable { onSelectSubject(sub.id) }
                    .padding(horizontal = 12.dp, vertical = 7.dp)
            ) {
                Text(text = sub.icon, fontSize = 14.sp)
                Spacer(modifier = Modifier.width(6.dp))
                Text(
                    text = sub.name,
                    color = if (isSelected) Color.White else Color(0xFFADB5BD),
                    fontSize = 13.sp,
                    fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium
                )
            }
        }

        // Add Subject Chip
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier
                .clip(RoundedCornerShape(16.dp))
                .background(Color(0xFF20232E))
                .clickable { onAddSubjectClick() }
                .padding(horizontal = 10.dp, vertical = 7.dp)
        ) {
            Icon(
                imageVector = Icons.Default.Add,
                contentDescription = "Ders Ekle",
                tint = Color(0xFF00ADB5),
                modifier = Modifier.size(16.dp)
            )
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text = "Ekle",
                color = Color(0xFF00ADB5),
                fontSize = 12.sp,
                fontWeight = FontWeight.SemiBold
            )
        }
    }
}
