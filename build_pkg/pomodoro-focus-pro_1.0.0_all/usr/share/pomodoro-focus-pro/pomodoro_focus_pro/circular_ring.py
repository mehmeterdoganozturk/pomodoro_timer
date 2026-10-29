import math
import cairo
from gi.repository import Gtk, Pango, PangoCairo

def hex_to_rgba(hex_code, alpha=1.0):
    hex_code = hex_code.lstrip('#')
    if len(hex_code) == 6:
        r = int(hex_code[0:2], 16) / 255.0
        g = int(hex_code[2:4], 16) / 255.0
        b = int(hex_code[4:6], 16) / 255.0
        return (r, g, b, alpha)
    return (1.0, 0.32, 0.32, alpha)

THEMES = {
    "focus": {
        "primary": (1.0, 0.32, 0.32, 1.0),
        "primary_rgb": "#FF5252",
        "secondary": (1.0, 0.46, 0.46, 0.25),
        "track": (1.0, 1.0, 1.0, 0.08),
        "title": "ODAKLANMA",
        "badge_color": (1.0, 0.32, 0.32, 0.9)
    },
    "short_break": {
        "primary": (0.06, 0.73, 0.51, 1.0),
        "primary_rgb": "#10B981",
        "secondary": (0.06, 0.73, 0.51, 0.25),
        "track": (1.0, 1.0, 1.0, 0.08),
        "title": "KISA MOLA",
        "badge_color": (0.06, 0.73, 0.51, 0.9)
    },
    "long_break": {
        "primary": (0.39, 0.40, 0.95, 1.0),
        "primary_rgb": "#6366F1",
        "secondary": (0.39, 0.40, 0.95, 0.25),
        "track": (1.0, 1.0, 1.0, 0.08),
        "title": "UZUN MOLA",
        "badge_color": (0.39, 0.40, 0.95, 0.9)
    }
}

class CircularProgressRing(Gtk.DrawingArea):
    def __init__(self, timer_engine, storage_manager):
        super().__init__()
        self.timer = timer_engine
        self.storage = storage_manager
        self.progress_ratio = 0.0
        self.time_str = "25:00"
        self.mode = "focus"
        self.cycle_step = 1
        self.total_cycle = 4

        self.current_subject = self.storage.get_selected_subject()

        self.set_content_width(280)
        self.set_content_height(280)
        self.set_draw_func(self._on_draw)

        self.timer.on_tick_callbacks.append(self._on_tick)
        self.timer.on_mode_change_callbacks.append(self._on_mode_change)

    def _on_tick(self, time_str: str, progress_ratio: float):
        self.time_str = time_str
        self.progress_ratio = progress_ratio
        self.queue_draw()

    def _on_mode_change(self, new_mode: str):
        self.mode = new_mode
        self.queue_draw()

    def update_subject(self, subject: dict):
        self.current_subject = subject
        self.queue_draw()

    def update_cycle_info(self, current: int, total: int):
        self.cycle_step = current
        self.total_cycle = total
        self.queue_draw()

    def _on_draw(self, area, cr: cairo.Context, width: int, height: int):
        cx = width / 2.0
        cy = height / 2.0
        size = min(width, height)
        radius = size * 0.40
        line_width = max(8.0, size * 0.045)

        theme = THEMES.get(self.mode, THEMES["focus"])

        # In focus mode, adopt active subject accent color
        if self.mode == "focus" and self.current_subject and "color" in self.current_subject:
            sub_col = self.current_subject["color"]
            r, g, b, _ = hex_to_rgba(sub_col, 1.0)
            glow_rgba = (r, g, b, 0.3)
            title_text = f"{self.current_subject.get('icon', '')} {self.current_subject.get('name', 'ODAK').upper()}"
        else:
            r, g, b, _ = theme["primary"]
            glow_rgba = theme["secondary"]
            title_text = theme["title"]

        # 1. Background subtle track circle
        tr, tg, tb, ta = theme["track"]
        cr.save()
        cr.set_line_width(line_width)
        cr.set_source_rgba(tr, tg, tb, ta)
        cr.arc(cx, cy, radius, 0, 2 * math.pi)
        cr.stroke()
        cr.restore()

        # 2. Foreground animated progress arc
        start_angle = -math.pi / 2.0
        fill_angle = self.progress_ratio * (2 * math.pi)
        end_angle = start_angle + fill_angle

        if self.progress_ratio > 0.005:
            # Glow
            cr.save()
            cr.set_line_width(line_width * 1.5)
            cr.set_line_cap(cairo.LINE_CAP_ROUND)
            gr, gg, gb, ga = glow_rgba
            cr.set_source_rgba(gr, gg, gb, ga)
            cr.arc(cx, cy, radius, start_angle, end_angle)
            cr.stroke()
            cr.restore()

            # Sharp Arc
            cr.save()
            cr.set_line_width(line_width)
            cr.set_line_cap(cairo.LINE_CAP_ROUND)
            cr.set_source_rgba(r, g, b, 1.0)
            cr.arc(cx, cy, radius, start_angle, end_angle)
            cr.stroke()
            cr.restore()

            # Head dot
            head_x = cx + radius * math.cos(end_angle)
            head_y = cy + radius * math.sin(end_angle)
            cr.save()
            cr.set_source_rgba(1.0, 1.0, 1.0, 0.95)
            cr.arc(head_x, head_y, line_width * 0.38, 0, 2 * math.pi)
            cr.fill()
            cr.restore()

        # 3. Center Digital Time Display
        time_layout = PangoCairo.create_layout(cr)
        font_size = max(18, int(size * 0.165))
        font_desc = Pango.FontDescription(f"Ubuntu, Inter, Cantarell, Sans Bold {font_size}")
        time_layout.set_font_description(font_desc)
        time_layout.set_text(self.time_str, -1)

        t_w, t_h = time_layout.get_pixel_size()
        cr.save()
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.96)
        cr.move_to(cx - t_w / 2.0, cy - t_h / 2.0 - size * 0.04)
        PangoCairo.show_layout(cr, time_layout)
        cr.restore()

        # 4. Mode / Subject Subtitle
        sub_layout = PangoCairo.create_layout(cr)
        sub_font_size = max(8, int(size * 0.042))
        sub_desc = Pango.FontDescription(f"Ubuntu, Inter, Sans Bold {sub_font_size}")
        sub_layout.set_font_description(sub_desc)
        sub_layout.set_text(title_text, -1)

        s_w, s_h = sub_layout.get_pixel_size()
        cr.save()
        cr.set_source_rgba(r, g, b, 0.95)
        cr.move_to(cx - s_w / 2.0, cy + size * 0.08)
        PangoCairo.show_layout(cr, sub_layout)
        cr.restore()

        # 5. Session Cycle Dots
        if size > 180:
            dot_count = max(2, min(8, self.total_cycle))
            active_step = (self.cycle_step % dot_count)
            dot_r = max(2.5, size * 0.012)
            dot_spacing = max(9.0, size * 0.045)
            total_dots_width = (dot_count - 1) * dot_spacing
            start_dots_x = cx - total_dots_width / 2.0
            dots_y = cy + size * 0.165

            for i in range(dot_count):
                dot_x = start_dots_x + i * dot_spacing
                cr.save()
                if i < active_step or (active_step == 0 and self.cycle_step > 0):
                    cr.set_source_rgba(r, g, b, 0.9)
                else:
                    cr.set_source_rgba(1.0, 1.0, 1.0, 0.2)
                cr.arc(dot_x, dots_y, dot_r, 0, 2 * math.pi)
                cr.fill()
                cr.restore()
