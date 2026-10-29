import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import GObject from 'gi://GObject';
import Clutter from 'gi://Clutter';
import St from 'gi://St';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';
import { Extension, gettext as _ } from 'resource:///org/gnome/shell/extensions/extension.js';

const BUS_NAME = 'com.github.erdogan.PomodoroFocusPro';
const OBJECT_PATH = '/com/github/erdogan/PomodoroFocusPro';

const PomodoroIface = `
<node>
  <interface name="com.github.erdogan.PomodoroFocusPro">
    <method name="ShowWindow"/>
    <method name="HideWindow"/>
    <method name="Toggle"/>
    <method name="Reset"/>
    <method name="Skip"/>
    <method name="Quit"/>
    <method name="GetStatus">
      <arg type="s" name="time_str" direction="out"/>
      <arg type="d" name="ratio" direction="out"/>
      <arg type="s" name="state" direction="out"/>
      <arg type="s" name="mode" direction="out"/>
      <arg type="s" name="subject_name" direction="out"/>
      <arg type="s" name="subject_icon" direction="out"/>
      <arg type="b" name="window_visible" direction="out"/>
    </method>
    <signal name="StatusChanged">
      <arg type="s" name="time_str"/>
      <arg type="d" name="ratio"/>
      <arg type="s" name="state"/>
      <arg type="s" name="mode"/>
      <arg type="s" name="subject_name"/>
      <arg type="s" name="subject_icon"/>
      <arg type="b" name="window_visible"/>
    </signal>
  </interface>
</node>`;

const PomodoroProxy = Gio.DBusProxy.makeProxyWrapper(PomodoroIface);

const PomodoroIndicator = GObject.registerClass(
class PomodoroIndicator extends PanelMenu.Button {
    _init() {
        super._init(0.0, 'Pomodoro Focus Pro');

        this._proxy = null;
        this._signalId = 0;
        this._pollTimerId = 0;
        this._isAppRunning = false;

        // Panel Container
        this._box = new St.BoxLayout({
            style_class: 'panel-status-indicators-box pomodoro-indicator-box'
        });

        this._iconLabel = new St.Label({
            text: '🍅',
            y_align: Clutter.ActorAlign.CENTER
        });

        this._timeLabel = new St.Label({
            text: 'Pomodoro',
            y_align: Clutter.ActorAlign.CENTER,
            style_class: 'pomodoro-time-label'
        });

        this._box.add_child(this._iconLabel);
        this._box.add_child(this._timeLabel);
        this.add_child(this._box);

        this._buildMenu();
        this._initDBus();
    }

    _buildMenu() {
        // Status Title
        this._statusItem = new PopupMenu.PopupMenuItem('🍅 Pomodoro Focus Pro', {
            reactive: false,
            can_focus: false
        });
        this.menu.addMenuItem(this._statusItem);

        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());

        // Toggle (Start / Pause)
        this._toggleItem = new PopupMenu.PopupMenuItem('▶️ Başlat / Duraklat');
        this._toggleItem.connect('activate', () => {
            this._callMethod('Toggle');
        });
        this.menu.addMenuItem(this._toggleItem);

        // Skip to next phase
        this._skipItem = new PopupMenu.PopupMenuItem('⏭️ Sonraki Aşama');
        this._skipItem.connect('activate', () => {
            this._callMethod('Skip');
        });
        this.menu.addMenuItem(this._skipItem);

        // Reset
        this._resetItem = new PopupMenu.PopupMenuItem('↺ Başa Al (Sıfırla)');
        this._resetItem.connect('activate', () => {
            this._callMethod('Reset');
        });
        this.menu.addMenuItem(this._resetItem);

        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());

        // Show/Hide Main Window
        this._windowItem = new PopupMenu.PopupMenuItem('🪟 Pencereyi Göster');
        this._windowItem.connect('activate', () => {
            this._showOrLaunchApp();
        });
        this.menu.addMenuItem(this._windowItem);

        // Quit Completely
        this._quitItem = new PopupMenu.PopupMenuItem('❌ Uygulamayı Kapat');
        this._quitItem.connect('activate', () => {
            this._callMethod('Quit');
            this._updateDisplayDisconnected();
        });
        this.menu.addMenuItem(this._quitItem);
    }

    _initDBus() {
        try {
            this._proxy = new PomodoroProxy(
                Gio.DBus.session,
                BUS_NAME,
                OBJECT_PATH,
                (proxy, error) => {
                    if (error) {
                        this._updateDisplayDisconnected();
                        return;
                    }
                    this._onProxyReady();
                }
            );
        } catch (e) {
            this._updateDisplayDisconnected();
        }

        // Periodic heartbeat poll to detect app open/close
        this._pollTimerId = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 2, () => {
            this._checkAppHeartbeat();
            return GLib.SOURCE_CONTINUE;
        });
    }

    _onProxyReady() {
        if (!this._proxy) return;

        // Connect to StatusChanged signal
        this._signalId = this._proxy.connectSignal('StatusChanged', (proxy, senderName, [timeStr, ratio, state, mode, subName, subIcon, isVis]) => {
            this._updateStatus(timeStr, ratio, state, mode, subName, subIcon, isVis);
        });

        // Pull initial status
        this._checkAppHeartbeat();
    }

    _checkAppHeartbeat() {
        if (!this._proxy) return;

        this._proxy.GetStatusRemote((result, error) => {
            if (error) {
                this._isAppRunning = false;
                this._updateDisplayDisconnected();
                return;
            }
            this._isAppRunning = true;
            const [timeStr, ratio, state, mode, subName, subIcon, isVis] = result;
            this._updateStatus(timeStr, ratio, state, mode, subName, subIcon, isVis);
        });
    }

    _updateStatus(timeStr, ratio, state, mode, subName, subIcon, isVis) {
        this._isAppRunning = true;

        // Top bar labels
        let icon = subIcon || '🍅';
        if (mode === 'short_break' || mode === 'long_break') {
            icon = '☕';
        } else if (mode === 'test') {
            icon = '📝';
        } else if (mode === 'stopwatch') {
            icon = '⏱️';
        }

        let statePrefix = '';
        if (state === 'paused') {
            statePrefix = '⏸ ';
        }

        this._iconLabel.set_text(icon);
        this._timeLabel.set_text(`${statePrefix}${timeStr}`);

        // Update popup menu items
        let stateText = 'Hazır';
        if (state === 'running') stateText = 'Çalışıyor';
        else if (state === 'paused') stateText = 'Duraklatıldı';

        let modeText = subName || 'Ders Çalışma';
        if (mode === 'short_break') modeText = 'Kısa Mola';
        else if (mode === 'long_break') modeText = 'Uzun Mola';
        else if (mode === 'test') modeText = `${subName} Testi`;
        else if (mode === 'stopwatch') modeText = 'Serbest Kronometre';

        this._statusItem.label.set_text(`${icon} ${modeText} • ${timeStr} (${stateText})`);

        if (state === 'running') {
            this._toggleItem.label.set_text('⏸️ Duraklat');
        } else {
            this._toggleItem.label.set_text('▶️ Başlat');
        }

        if (isVis) {
            this._windowItem.label.set_text('🙈 Pencereyi Gizle');
        } else {
            this._windowItem.label.set_text('🪟 Pencereyi Göster');
        }
    }

    _updateDisplayDisconnected() {
        this._isAppRunning = false;
        this._iconLabel.set_text('🍅');
        this._timeLabel.set_text('Pomodoro');
        this._statusItem.label.set_text('🍅 Pomodoro (Kapalı - Başlatmak için Tıkla)');
        this._toggleItem.label.set_text('▶️ Başlat');
        this._windowItem.label.set_text('🚀 Uygulamayı Başlat');
    }

    _callMethod(methodName) {
        if (!this._proxy) return;

        if (!this._isAppRunning && methodName === 'Toggle') {
            this._showOrLaunchApp();
            return;
        }

        try {
            if (typeof this._proxy[`${methodName}Remote`] === 'function') {
                this._proxy[`${methodName}Remote`](() => {});
            }
        } catch (e) {
            log(`[PomodoroFocusPro] Error calling ${methodName}: ${e}`);
        }
    }

    _showOrLaunchApp() {
        if (this._isAppRunning) {
            this._callMethod('ShowWindow');
        } else {
            // Launch app process
            try {
                let launcher = Gio.Subprocess.new(
                    ['pomodoro-focus-pro'],
                    Gio.SubprocessFlags.NONE
                );
            } catch (e) {
                // Fallback direct path
                let home = GLib.get_home_dir();
                Gio.Subprocess.new(
                    [`${home}/.local/bin/pomodoro-focus-pro`],
                    Gio.SubprocessFlags.NONE
                );
            }
        }
    }

    destroy() {
        if (this._pollTimerId) {
            GLib.Source.remove(this._pollTimerId);
            this._pollTimerId = 0;
        }
        if (this._proxy && this._signalId) {
            this._proxy.disconnectSignal(this._signalId);
            this._signalId = 0;
        }
        this._proxy = null;
        super.destroy();
    }
});

export default class PomodoroFocusProExtension extends Extension {
    enable() {
        this._indicator = new PomodoroIndicator();
        // Add to right side of top bar status area
        Main.panel.addToStatusArea(this.metadata.uuid, this._indicator, 1, 'right');
    }

    disable() {
        if (this._indicator) {
            this._indicator.destroy();
            this._indicator = null;
        }
    }
}
