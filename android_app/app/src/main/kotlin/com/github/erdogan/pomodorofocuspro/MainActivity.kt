/*
 * Copyright (c) 2026 Mehmet Erdoğan Öztürk <mehmeterdoganozturk@gmail.com>
 * Licensed under the MIT License. See LICENSE in the project root for details.
 */

package com.github.erdogan.pomodorofocuspro

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.github.erdogan.pomodorofocuspro.ui.theme.PomodoroFocusProTheme

class MainActivity : ComponentActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    enableEdgeToEdge()
    setContent {
      PomodoroFocusProTheme { Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) { MainNavigation() } }
    }
  }
}
