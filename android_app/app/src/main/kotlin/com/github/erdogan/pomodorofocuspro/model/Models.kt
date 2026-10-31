package com.github.erdogan.pomodorofocuspro.model

import androidx.compose.ui.graphics.Color
import kotlinx.serialization.Serializable

enum class TimerMode(
    val id: String,
    val title: String,
    val icon: String,
    val defaultMinutes: Int,
    val accentColor: Long
) {
    POMODORO("focus", "Pomodoro", "🍅", 25, 0xFFFF5252),
    SHORT_BREAK("short_break", "Kısa Mola", "☕", 5, 0xFF10B981),
    LONG_BREAK("long_break", "Uzun Mola", "🌴", 15, 0xFF6366F1),
    TEST("test", "Test / Sınav", "📝", 20, 0xFFF59E0B),
    STOPWATCH("stopwatch", "Kronometre", "⏱️", 0, 0xFF06B6D4);

    fun getColor(): Color = Color(accentColor)
}

enum class TimerState {
    STOPPED,
    RUNNING,
    PAUSED
}

@Serializable
data class Subject(
    val id: String,
    val name: String,
    val icon: String = "📖",
    val colorHex: String = "#3B82F6",
    val badge: String = "Genel",
    val visible: Boolean = true
) {
    fun parseColor(): Color {
        return try {
            val clean = colorHex.removePrefix("#")
            val colorInt = clean.toLong(16) or 0x00000000FF000000
            Color(colorInt)
        } catch (_: Exception) {
            Color(0xFF3B82F6)
        }
    }
}

@Serializable
data class WorkspaceProfile(
    val id: String,
    val name: String,
    val description: String,
    val defaultFocus: Int = 25,
    val defaultShortBreak: Int = 5,
    val defaultLongBreak: Int = 15,
    val defaultDailyGoal: Int = 8,
    val subjects: List<Subject>
)

@Serializable
data class PomodoroConfig(
    val activeProfileId: String = "yks",
    val selectedSubjectId: String = "mat",
    val focusDuration: Int = 25,
    val testDuration: Int = 20,
    val shortBreakDuration: Int = 5,
    val longBreakDuration: Int = 15,
    val longBreakInterval: Int = 4,
    val dailyGoal: Int = 8,
    val soundEnabled: Boolean = true,
    val vibrateEnabled: Boolean = true,
    val autoStartBreaks: Boolean = false,
    val autoStartPomodoros: Boolean = false,
    val profiles: Map<String, WorkspaceProfile> = emptyMap()
)

@Serializable
data class DailyRecord(
    val date: String, // YYYY-MM-DD
    val completedSessions: Int = 0,
    val focusMinutes: Int = 0,
    val breakCount: Int = 0,
    val subjectMinutes: Map<String, Int> = emptyMap()
)

object DefaultData {
    fun createDefaultProfiles(): Map<String, WorkspaceProfile> {
        val yks = WorkspaceProfile(
            id = "yks",
            name = "🎓 YKS / Sınav Hazırlık",
            description = "Matematik, Geometri, Fizik, Kimya, Paragraf ve Deneme",
            defaultFocus = 25,
            defaultShortBreak = 5,
            defaultLongBreak = 15,
            defaultDailyGoal = 8,
            subjects = listOf(
                Subject("mat", "Matematik", "📐", "#3B82F6", "AYT/TYT", true),
                Subject("geo", "Geometri", "📏", "#06B6D4", "AYT/TYT", true),
                Subject("fiz", "Fizik", "🔬", "#F59E0B", "AYT/TYT", true),
                Subject("kim", "Kimya", "🧪", "#10B981", "AYT/TYT", true),
                Subject("turk", "TYT Paragraf / Türkçe", "📖", "#EC4899", "TYT", true),
                Subject("biy", "Biyoloji", "🧬", "#84CC16", "AYT/TYT", true),
                Subject("deneme", "Deneme Sınavı", "📝", "#8B5CF6", "Genel", true)
            )
        )

        val engineering = WorkspaceProfile(
            id = "engineering",
            name = "💻 Mühendislik & IT",
            description = "Kodlama, Algoritma, Sistem Mimarisi ve Debugging",
            defaultFocus = 50,
            defaultShortBreak = 10,
            defaultLongBreak = 20,
            defaultDailyGoal = 6,
            subjects = listOf(
                Subject("code", "Kodlama / Proje", "💻", "#6366F1", "Dev", true),
                Subject("algo", "Algoritma & Problem", "⚡", "#F59E0B", "LeetCode", true),
                Subject("arch", "Sistem Mimarisi", "🏗️", "#06B6D4", "Design", true),
                Subject("debug", "Bugfix & Debugging", "🐛", "#EF4444", "Fix", true),
                Subject("docs", "Teknik Dokümantasyon", "📚", "#10B981", "Docs", true),
                Subject("infra", "DevOps & Sunucu", "⚙️", "#8B5CF6", "Infra", true)
            )
        )

        val business = WorkspaceProfile(
            id = "business",
            name = "💼 İş & Yönetim",
            description = "Strateji, Toplantı, Raporlama ve Operasyon",
            defaultFocus = 30,
            defaultShortBreak = 5,
            defaultLongBreak = 15,
            defaultDailyGoal = 6,
            subjects = listOf(
                Subject("strat", "Strateji & Planlama", "🎯", "#3B82F6", "Plan", true),
                Subject("meet", "Toplantı & İletişim", "👥", "#8B5CF6", "Team", true),
                Subject("report", "Raporlama & Analiz", "📊", "#10B981", "Data", true),
                Subject("tasks", "Operasyon & Görevler", "📋", "#F59E0B", "Ops", true),
                Subject("emails", "E-Posta & İletişim", "✉️", "#EC4899", "Mail", true)
            )
        )

        return mapOf(
            "yks" to yks,
            "engineering" to engineering,
            "business" to business
        )
    }
}
