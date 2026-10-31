package com.github.erdogan.pomodorofocuspro.ui.main

import androidx.activity.ComponentActivity
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithText
import org.junit.Rule
import org.junit.Test

class MainScreenTest {

    @get:Rule
    val composeTestRule = createAndroidComposeRule<ComponentActivity>()

    @Test
    fun app_starts_successfully() {
        // App starts and displays title
        composeTestRule.setContent {
            MainScreen()
        }
        composeTestRule.onNodeWithText("Pomodoro Pro").assertExists()
    }
}
