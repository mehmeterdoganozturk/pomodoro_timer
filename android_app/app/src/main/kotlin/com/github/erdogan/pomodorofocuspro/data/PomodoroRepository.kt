package com.github.erdogan.pomodorofocuspro.data

import android.content.Context
import android.content.SharedPreferences
import com.github.erdogan.pomodorofocuspro.model.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import org.json.JSONArray
import org.json.JSONObject
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Date
import java.util.Locale

class PomodoroRepository(context: Context) {

    private val prefs: SharedPreferences =
        context.getSharedPreferences("pomodoro_focus_pro_prefs", Context.MODE_PRIVATE)

    private val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())

    private val _configFlow = MutableStateFlow(loadConfig())
    val configFlow: StateFlow<PomodoroConfig> = _configFlow.asStateFlow()

    private val _todayRecordFlow = MutableStateFlow(getRecordForDate(getTodayDateStr()))
    val todayRecordFlow: StateFlow<DailyRecord> = _todayRecordFlow.asStateFlow()

    fun getTodayDateStr(): String = dateFormat.format(Date())

    fun loadConfig(): PomodoroConfig {
        val raw = prefs.getString("config_json", null)
        val defaultProfiles = DefaultData.createDefaultProfiles()

        if (raw.isNullOrEmpty()) {
            val cfg = PomodoroConfig(profiles = defaultProfiles)
            saveConfig(cfg)
            return cfg
        }

        return try {
            val json = JSONObject(raw)
            val activeProfile = json.optString("activeProfileId", "yks")
            val selectedSubject = json.optString("selectedSubjectId", "mat")
            val focusDur = json.optInt("focusDuration", 25)
            val testDur = json.optInt("testDuration", 20)
            val shortDur = json.optInt("shortBreakDuration", 5)
            val longDur = json.optInt("longBreakDuration", 15)
            val longInterval = json.optInt("longBreakInterval", 4)
            val goal = json.optInt("dailyGoal", 8)
            val sound = json.optBoolean("soundEnabled", true)
            val vibrate = json.optBoolean("vibrateEnabled", true)
            val autoBreak = json.optBoolean("autoStartBreaks", false)
            val autoPomo = json.optBoolean("autoStartPomodoros", false)

            val profilesMap = mutableMapOf<String, WorkspaceProfile>()
            val profilesObj = json.optJSONObject("profiles")
            if (profilesObj != null) {
                val keys = profilesObj.keys()
                while (keys.hasNext()) {
                    val k = keys.next()
                    val pObj = profilesObj.getJSONObject(k)
                    val subjectsList = mutableListOf<Subject>()
                    val subArray = pObj.optJSONArray("subjects")
                    if (subArray != null) {
                        for (i in 0 until subArray.length()) {
                            val sObj = subArray.getJSONObject(i)
                            subjectsList.add(
                                Subject(
                                    id = sObj.getString("id"),
                                    name = sObj.getString("name"),
                                    icon = sObj.optString("icon", "📖"),
                                    colorHex = sObj.optString("colorHex", "#3B82F6"),
                                    badge = sObj.optString("badge", "Genel"),
                                    visible = sObj.optBoolean("visible", true)
                                )
                            )
                        }
                    }
                    profilesMap[k] = WorkspaceProfile(
                        id = pObj.getString("id"),
                        name = pObj.getString("name"),
                        description = pObj.optString("description", ""),
                        defaultFocus = pObj.optInt("defaultFocus", 25),
                        defaultShortBreak = pObj.optInt("defaultShortBreak", 5),
                        defaultLongBreak = pObj.optInt("defaultLongBreak", 15),
                        defaultDailyGoal = pObj.optInt("defaultDailyGoal", 8),
                        subjects = subjectsList
                    )
                }
            } else {
                profilesMap.putAll(defaultProfiles)
            }

            PomodoroConfig(
                activeProfileId = activeProfile,
                selectedSubjectId = selectedSubject,
                focusDuration = focusDur,
                testDuration = testDur,
                shortBreakDuration = shortDur,
                longBreakDuration = longDur,
                longBreakInterval = longInterval,
                dailyGoal = goal,
                soundEnabled = sound,
                vibrateEnabled = vibrate,
                autoStartBreaks = autoBreak,
                autoStartPomodoros = autoPomo,
                profiles = if (profilesMap.isEmpty()) defaultProfiles else profilesMap
            )
        } catch (_: Exception) {
            PomodoroConfig(profiles = defaultProfiles)
        }
    }

    fun saveConfig(config: PomodoroConfig) {
        val json = JSONObject().apply {
            put("activeProfileId", config.activeProfileId)
            put("selectedSubjectId", config.selectedSubjectId)
            put("focusDuration", config.focusDuration)
            put("testDuration", config.testDuration)
            put("shortBreakDuration", config.shortBreakDuration)
            put("longBreakDuration", config.longBreakDuration)
            put("longBreakInterval", config.longBreakInterval)
            put("dailyGoal", config.dailyGoal)
            put("soundEnabled", config.soundEnabled)
            put("vibrateEnabled", config.vibrateEnabled)
            put("autoStartBreaks", config.autoStartBreaks)
            put("autoStartPomodoros", config.autoStartPomodoros)

            val profilesObj = JSONObject()
            config.profiles.forEach { (id, profile) ->
                val pObj = JSONObject().apply {
                    put("id", profile.id)
                    put("name", profile.name)
                    put("description", profile.description)
                    put("defaultFocus", profile.defaultFocus)
                    put("defaultShortBreak", profile.defaultShortBreak)
                    put("defaultLongBreak", profile.defaultLongBreak)
                    put("defaultDailyGoal", profile.defaultDailyGoal)

                    val subArr = JSONArray()
                    profile.subjects.forEach { s ->
                        val sObj = JSONObject().apply {
                            put("id", s.id)
                            put("name", s.name)
                            put("icon", s.icon)
                            put("colorHex", s.colorHex)
                            put("badge", s.badge)
                            put("visible", s.visible)
                        }
                        subArr.put(sObj)
                    }
                    put("subjects", subArr)
                }
                profilesObj.put(id, pObj)
            }
            put("profiles", profilesObj)
        }

        prefs.edit().putString("config_json", json.toString()).apply()
        _configFlow.value = config
    }

    fun getRecordForDate(dateStr: String): DailyRecord {
        val raw = prefs.getString("day_$dateStr", null) ?: return DailyRecord(date = dateStr)
        return try {
            val obj = JSONObject(raw)
            val sessions = obj.optInt("completedSessions", 0)
            val focusMins = obj.optInt("focusMinutes", 0)
            val breaks = obj.optInt("breakCount", 0)
            val subMap = mutableMapOf<String, Int>()
            val subObj = obj.optJSONObject("subjectMinutes")
            if (subObj != null) {
                val it = subObj.keys()
                while (it.hasNext()) {
                    val k = it.next()
                    subMap[k] = subObj.getInt(k)
                }
            }
            DailyRecord(
                date = dateStr,
                completedSessions = sessions,
                focusMinutes = focusMins,
                breakCount = breaks,
                subjectMinutes = subMap
            )
        } catch (_: Exception) {
            DailyRecord(date = dateStr)
        }
    }

    fun saveRecord(record: DailyRecord) {
        val obj = JSONObject().apply {
            put("date", record.date)
            put("completedSessions", record.completedSessions)
            put("focusMinutes", record.focusMinutes)
            put("breakCount", record.breakCount)
            val subObj = JSONObject()
            record.subjectMinutes.forEach { (k, v) -> subObj.put(k, v) }
            put("subjectMinutes", subObj)
        }
        prefs.edit().putString("day_${record.date}", obj.toString()).apply()
        if (record.date == getTodayDateStr()) {
            _todayRecordFlow.value = record
        }
    }

    fun recordCompletedSession(mode: TimerMode, subjectId: String, durationMinutes: Int) {
        val todayStr = getTodayDateStr()
        val current = getRecordForDate(todayStr)

        val updated = when (mode) {
            TimerMode.POMODORO, TimerMode.TEST -> {
                val subMap = current.subjectMinutes.toMutableMap()
                val oldMins = subMap[subjectId] ?: 0
                subMap[subjectId] = oldMins + durationMinutes
                current.copy(
                    completedSessions = current.completedSessions + 1,
                    focusMinutes = current.focusMinutes + durationMinutes,
                    subjectMinutes = subMap
                )
            }
            TimerMode.STOPWATCH -> {
                val subMap = current.subjectMinutes.toMutableMap()
                val oldMins = subMap[subjectId] ?: 0
                subMap[subjectId] = oldMins + durationMinutes
                current.copy(
                    focusMinutes = current.focusMinutes + durationMinutes,
                    subjectMinutes = subMap
                )
            }
            TimerMode.SHORT_BREAK, TimerMode.LONG_BREAK -> {
                current.copy(
                    breakCount = current.breakCount + 1
                )
            }
        }
        saveRecord(updated)
    }

    /**
     * Calculates the streak (Zincir) based on consecutive days meeting the daily goal.
     */
    fun calculateStreak(dailyGoal: Int): Pair<Int, Int> {
        val cal = Calendar.getInstance()
        var currentStreak = 0
        var maxStreak = 0
        var tempStreak = 0

        // Check back up to 365 days
        for (i in 0 until 365) {
            val dStr = dateFormat.format(cal.time)
            val record = getRecordForDate(dStr)

            if (record.completedSessions >= dailyGoal) {
                tempStreak++
                if (i == 0 || currentStreak == i) {
                    currentStreak = tempStreak
                }
                if (tempStreak > maxStreak) {
                    maxStreak = tempStreak
                }
            } else {
                if (i == 0) {
                    // Today might not be finished yet, so check yesterday for active streak
                    // We continue checking backwards
                } else {
                    tempStreak = 0
                }
            }
            cal.add(Calendar.DAY_OF_YEAR, -1)
        }

        return Pair(currentStreak, maxOf(currentStreak, maxStreak))
    }

    /**
     * Returns last 28 days for the Heatmap (4 weeks x 7 days)
     */
    fun getLast28Days(): List<Pair<Date, DailyRecord>> {
        val result = mutableListOf<Pair<Date, DailyRecord>>()
        val cal = Calendar.getInstance()

        for (i in 27 downTo 0) {
            val dayCal = Calendar.getInstance().apply {
                time = cal.time
                add(Calendar.DAY_OF_YEAR, -i)
            }
            val dStr = dateFormat.format(dayCal.time)
            result.add(Pair(dayCal.time, getRecordForDate(dStr)))
        }
        return result
    }
}
