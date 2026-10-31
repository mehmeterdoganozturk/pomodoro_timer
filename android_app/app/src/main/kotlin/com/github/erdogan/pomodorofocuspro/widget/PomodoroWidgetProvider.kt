package com.github.erdogan.pomodorofocuspro.widget

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.widget.RemoteViews
import com.github.erdogan.pomodorofocuspro.MainActivity
import com.github.erdogan.pomodorofocuspro.R
import com.github.erdogan.pomodorofocuspro.data.PomodoroRepository
import com.github.erdogan.pomodorofocuspro.engine.TimerEngine
import com.github.erdogan.pomodorofocuspro.model.TimerState

class PomodoroWidgetProvider : AppWidgetProvider() {

    companion object {
        const val ACTION_WIDGET_TOGGLE = "com.github.erdogan.pomodoro.WIDGET_TOGGLE"
        const val ACTION_WIDGET_RESET = "com.github.erdogan.pomodoro.WIDGET_RESET"

        fun updateAllWidgets(context: Context) {
            try {
                val appWidgetManager = AppWidgetManager.getInstance(context) ?: return
                val thisWidget = ComponentName(context, PomodoroWidgetProvider::class.java)
                val appWidgetIds = appWidgetManager.getAppWidgetIds(thisWidget)
                for (id in appWidgetIds) {
                    updateAppWidget(context, appWidgetManager, id)
                }
            } catch (_: Exception) {}
        }

        fun updateAppWidget(
            context: Context,
            appWidgetManager: AppWidgetManager,
            appWidgetId: Int
        ) {
            try {
                TimerEngine.init(context)
                val views = RemoteViews(context.packageName, R.layout.widget_pomodoro)
                val repo = PomodoroRepository(context)
                val config = repo.loadConfig()
                val state = TimerEngine.stateFlow.value

                // 1. Digital Time
                views.setTextViewText(R.id.widget_timer_text, state.formattedTime)

                // 2. Active Subject Badge
                val activeProfile = config.profiles[config.activeProfileId]
                val activeSubject = activeProfile?.subjects?.find { it.id == config.selectedSubjectId }
                val subName = activeSubject?.name ?: "Genel"
                val subIcon = activeSubject?.icon ?: "📖"
                views.setTextViewText(R.id.widget_subject_badge, "$subIcon $subName")

                // 3. Streak Badge
                val streakPair = repo.calculateStreak(config.dailyGoal)
                views.setTextViewText(R.id.widget_streak_badge, "🔥 ${streakPair.first} Gün")

                // 4. Status Subtitle
                val isRunning = state.state == TimerState.RUNNING
                val cycleIndex = (state.sessionCount % config.longBreakInterval) + 1
                val subtitle = "${state.mode.icon} ${state.mode.title} • Döngü: $cycleIndex/${config.longBreakInterval} • Hedef: ${config.dailyGoal}"
                views.setTextViewText(R.id.widget_status_text, subtitle)

                // 5. Play / Pause Button Text
                val toggleText = if (isRunning) "⏸️ Duraklat" else "▶️ Başlat"
                views.setTextViewText(R.id.widget_btn_toggle, toggleText)

                // 6. PendingIntent for Open App (click root or open button)
                val openAppIntent = Intent(context, MainActivity::class.java).apply {
                    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
                }
                val openAppPendingIntent = PendingIntent.getActivity(
                    context,
                    0,
                    openAppIntent,
                    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
                )
                views.setOnClickPendingIntent(R.id.widget_root, openAppPendingIntent)
                views.setOnClickPendingIntent(R.id.widget_btn_open, openAppPendingIntent)

                // 7. PendingIntent for Play / Pause Toggle (Broadcast)
                val toggleIntent = Intent(context, PomodoroWidgetProvider::class.java).apply {
                    action = ACTION_WIDGET_TOGGLE
                }
                val togglePendingIntent = PendingIntent.getBroadcast(
                    context,
                    10,
                    toggleIntent,
                    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
                )
                views.setOnClickPendingIntent(R.id.widget_btn_toggle, togglePendingIntent)

                // 8. PendingIntent for Reset (Broadcast)
                val resetIntent = Intent(context, PomodoroWidgetProvider::class.java).apply {
                    action = ACTION_WIDGET_RESET
                }
                val resetPendingIntent = PendingIntent.getBroadcast(
                    context,
                    11,
                    resetIntent,
                    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
                )
                views.setOnClickPendingIntent(R.id.widget_btn_reset, resetPendingIntent)

                appWidgetManager.updateAppWidget(appWidgetId, views)
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        for (appWidgetId in appWidgetIds) {
            updateAppWidget(context, appWidgetManager, appWidgetId)
        }
    }

    override fun onReceive(context: Context, intent: Intent) {
        super.onReceive(context, intent)
        TimerEngine.init(context)

        when (intent.action) {
            ACTION_WIDGET_TOGGLE -> {
                TimerEngine.toggleStartPause(context)
                updateAllWidgets(context)
            }
            ACTION_WIDGET_RESET -> {
                TimerEngine.reset(context)
                updateAllWidgets(context)
            }
            else -> {
                updateAllWidgets(context)
            }
        }
    }
}
