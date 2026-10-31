package com.github.erdogan.pomodorofocuspro.ui.main

import com.github.erdogan.pomodorofocuspro.model.DefaultData
import com.github.erdogan.pomodorofocuspro.model.PomodoroConfig
import com.github.erdogan.pomodorofocuspro.model.TimerMode
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test

class ModelUnitTest {
    @Test
    fun defaultProfiles_areProperlyInitialized() {
        val profiles = DefaultData.createDefaultProfiles()
        assertTrue(profiles.containsKey("yks"))
        assertTrue(profiles.containsKey("engineering"))
        assertTrue(profiles.containsKey("business"))

        val yks = profiles["yks"]
        assertNotNull(yks)
        assertTrue(yks!!.subjects.isNotEmpty())
    }

    @Test
    fun timerMode_hasCorrectDefaults() {
        assertEquals(25, TimerMode.POMODORO.defaultMinutes)
        assertEquals(5, TimerMode.SHORT_BREAK.defaultMinutes)
        assertEquals(15, TimerMode.LONG_BREAK.defaultMinutes)
        assertEquals(20, TimerMode.TEST.defaultMinutes)
        assertEquals(0, TimerMode.STOPWATCH.defaultMinutes)
    }

    @Test
    fun pomodoroConfig_defaultValuesAreValid() {
        val config = PomodoroConfig()
        assertEquals("yks", config.activeProfileId)
        assertEquals(25, config.focusDuration)
        assertEquals(8, config.dailyGoal)
    }
}
