import cairo
from gi.repository import Gtk, Pango, PangoCairo

LEVEL_COLORS = {
    0: (0.14, 0.15, 0.20, 1.0),   # #242633 (No study)
    1: (0.08, 0.33, 0.18, 1.0),   # #14532D (Light)
    2: (0.08, 0.50, 0.24, 1.0),   # #15803D (Medium)
    3: (0.13, 0.77, 0.37, 1.0),   # #22C55E (High)
    4: (0.29, 0.87, 0.50, 1.0)    # #4ADE80 (Goal achieved)
}

class HeatmapWidget(Gtk.DrawingArea):
    def __init__(self, storage_manager):
        super().__init__()
        self.storage = storage_manager
        self.days_data = []

        self.set_content_width(340)
        self.set_content_height(140)
        self.set_draw_func(self._on_draw)

        self.refresh()

    def refresh(self):
        self.days_data = self.storage.get_past_days_data(count=28) # 4 weeks
        self.queue_draw()

    def _on_draw(self, area, cr: cairo.Context, width: int, height: int):
        cols = 7  # 7 days per week
        rows = 4  # 4 weeks
        cell_size = 28.0
        gap = 8.0

        total_w = cols * cell_size + (cols - 1) * gap
        total_h = rows * cell_size + (rows - 1) * gap

        start_x = (width - total_w) / 2.0
        start_y = 12.0

        if not self.days_data or len(self.days_data) < 28:
            return

        for idx, item in enumerate(self.days_data):
            r_idx = idx // cols
            c_idx = idx % cols

            x = start_x + c_idx * (cell_size + gap)
            y = start_y + r_idx * (cell_size + gap)

            lvl = item.get("level", 0)
            is_today = item.get("is_today", False)
            day_num = item.get("day_num", 1)

            # Draw cell rounded rectangle
            cr.save()
            r, g, b, a = LEVEL_COLORS.get(lvl, LEVEL_COLORS[0])
            cr.set_source_rgba(r, g, b, a)

            # Rounded rect path
            radius = 6.0
            cr.new_sub_path()
            cr.arc(x + cell_size - radius, y + radius, radius, -1.5708, 0)
            cr.arc(x + cell_size - radius, y + cell_size - radius, radius, 0, 1.5708)
            cr.arc(x + radius, y + cell_size - radius, radius, 1.5708, 3.1416)
            cr.arc(x + radius, y + radius, radius, 3.1416, 4.7124)
            cr.close_path()
            cr.fill_preserve()

            # Border
            if is_today:
                cr.set_source_rgba(1.0, 0.8, 0.2, 0.9)  # Golden highlight for today
                cr.set_line_width(2.0)
            else:
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.08)
                cr.set_line_width(1.0)
            cr.stroke()
            cr.restore()

            # Number label inside cell
            layout = PangoCairo.create_layout(cr)
            font_desc = Pango.FontDescription("Ubuntu, Inter, Sans Bold 8")
            layout.set_font_description(font_desc)
            layout.set_text(str(day_num), -1)
            t_w, t_h = layout.get_pixel_size()

            cr.save()
            if lvl >= 2:
                cr.set_source_rgba(0.05, 0.1, 0.05, 0.9)
            else:
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.5)
            cr.move_to(x + (cell_size - t_w) / 2.0, y + (cell_size - t_h) / 2.0)
            PangoCairo.show_layout(cr, layout)
            cr.restore()
