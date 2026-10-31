package com.github.erdogan.pomodorofocuspro.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import com.github.erdogan.pomodorofocuspro.MainActivity
import com.github.erdogan.pomodorofocuspro.R
import com.github.erdogan.pomodorofocuspro.data.PomodoroRepository
import com.github.erdogan.pomodorofocuspro.engine.TimerEngine
import com.github.erdogan.pomodorofocuspro.model.TimerState

class TimerService : Service() {

    companion object {
        const val CHANNEL_ID = "pomodoro_timer_channel"
        const val NOTIFICATION_ID = 1001

        const val ACTION_START = "com.github.erdogan.pomodoro.ACTION_START"
        const val ACTION_PAUSE = "com.github.erdogan.pomodoro.ACTION_PAUSE"
        const val ACTION_TOGGLE = "com.github.erdogan.pomodoro.ACTION_TOGGLE"
        const val ACTION_RESET = "com.github.erdogan.pomodoro.ACTION_RESET"
        const val ACTION_SKIP = "com.github.erdogan.pomodoro.ACTION_SKIP"
        const val ACTION_SYNC = "com.github.erdogan.pomodoro.ACTION_SYNC"
        const val ACTION_UPDATE_NOTIFICATION = "com.github.erdogan.pomodoro.ACTION_UPDATE_NOTIF"
    }

    private lateinit var repository: PomodoroRepository

    override fun onCreate() {
        super.onCreate()
        repository = PomodoroRepository(this)
        TimerEngine.init(this)
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val action = intent?.action ?: ACTION_SYNC

        when (action) {
            ACTION_START -> TimerEngine.start(this)
            ACTION_PAUSE -> TimerEngine.pause(this)
            ACTION_TOGGLE -> TimerEngine.toggleStartPause(this)
            ACTION_RESET -> TimerEngine.reset(this)
            ACTION_SKIP -> TimerEngine.skipNext(this)
            ACTION_SYNC, ACTION_UPDATE_NOTIFICATION -> {
                // Just sync notification
            }
        }

        val state = TimerEngine.stateFlow.value
        if (state.state == TimerState.RUNNING) {
            val notif = buildNotification()
            startForeground(NOTIFICATION_ID, notif)
        } else if (state.state == TimerState.PAUSED) {
            val notif = buildNotification()
            val nm = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            nm.notify(NOTIFICATION_ID, notif)
        } else {
            stopForeground(STOP_FOREGROUND_REMOVE)
            stopSelf()
        }

        return START_NOT_STICKY
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Pomodoro Pro Sayacı",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Aktif sayaç geri sayımı ve bildirimleri"
                setShowBadge(false)
            }
            val nm = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            nm.createNotificationChannel(channel)
        }
    }

    private fun buildNotification(): Notification {
        val state = TimerEngine.stateFlow.value
        val config = repository.loadConfig()
        val activeProfile = config.profiles[config.activeProfileId]
        val activeSubject = activeProfile?.subjects?.find { it.id == config.selectedSubjectId }

        val subjectName = activeSubject?.name ?: "Genel"
        val subjectIcon = activeSubject?.icon ?: "🍅"

        val openAppIntent = Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }
        val openAppPendingIntent = PendingIntent.getActivity(
            this,
            0,
            openAppIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val toggleIntent = Intent(this, TimerService::class.java).apply {
            action = ACTION_TOGGLE
        }
        val togglePendingIntent = PendingIntent.getService(
            this,
            1,
            toggleIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val resetIntent = Intent(this, TimerService::class.java).apply {
            action = ACTION_RESET
        }
        val resetPendingIntent = PendingIntent.getService(
            this,
            2,
            resetIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val isRunning = state.state == TimerState.RUNNING
        val toggleTitle = if (isRunning) "⏸️ Duraklat" else "▶️ Başlat"

        val title = "${state.mode.icon} ${state.formattedTime} • $subjectIcon $subjectName"
        val statusText = when (state.state) {
            TimerState.RUNNING -> "${state.mode.title} devam ediyor..."
            TimerState.PAUSED -> "Sayaç duraklatıldı."
            TimerState.STOPPED -> "Sayaç hazır."
        }

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setContentTitle(title)
            .setContentText(statusText)
            .setContentIntent(openAppPendingIntent)
            .setOngoing(isRunning)
            .setOnlyAlertOnce(true)
            .addAction(0, toggleTitle, togglePendingIntent)
            .addAction(0, "🔄 Sıfırla", resetPendingIntent)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
