package com.github.erdogan.pomodorofocuspro.util

import android.content.Context
import android.media.AudioAttributes
import android.media.MediaPlayer
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import com.github.erdogan.pomodorofocuspro.R

class SoundHelper(private val context: Context) {

    private fun getVibrator(): Vibrator {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            val vibratorManager = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as VibratorManager
            vibratorManager.defaultVibrator
        } else {
            @Suppress("DEPRECATION")
            context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
        }
    }

    fun playFocusComplete(soundEnabled: Boolean, vibrateEnabled: Boolean) {
        if (vibrateEnabled) {
            vibratePattern(longArrayOf(0, 300, 150, 300))
        }
        if (soundEnabled) {
            playSound(R.raw.focus_complete)
        }
    }

    fun playBreakComplete(soundEnabled: Boolean, vibrateEnabled: Boolean) {
        if (vibrateEnabled) {
            vibratePattern(longArrayOf(0, 200, 100, 200, 100, 200))
        }
        if (soundEnabled) {
            playSound(R.raw.break_complete)
        }
    }

    private fun playSound(resId: Int) {
        try {
            val player = MediaPlayer.create(context, resId) ?: return
            player.setAudioAttributes(
                AudioAttributes.Builder()
                    .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                    .setUsage(AudioAttributes.USAGE_ALARM)
                    .build()
            )
            player.setOnCompletionListener {
                it.release()
            }
            player.start()
        } catch (_: Exception) {
        }
    }

    private fun vibratePattern(pattern: LongArray) {
        try {
            val vibrator = getVibrator()
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                vibrator.vibrate(VibrationEffect.createWaveform(pattern, -1))
            } else {
                @Suppress("DEPRECATION")
                vibrator.vibrate(pattern, -1)
            }
        } catch (_: Exception) {
        }
    }
}
