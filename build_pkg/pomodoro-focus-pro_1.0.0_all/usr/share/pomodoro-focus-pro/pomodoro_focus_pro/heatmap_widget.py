import cairo
from gi.repository import Gtk, Pango, PangoCairo

LEVEL_COLORS = {
    -1: (0.10, 0.11, 0.15, 0.45),  # Future day (muted)
    0: (0.14, 0.15, 0.20, 1.0),    # No study (#242633)
    1: (0.08, 0.33, 0.18, 1.0),    # Light (#14532D)
    2: (0.08, 0.50, 0.24, 1.0),    # Medium (#15803D)
    3: (0.13, 0.77, 0.37, 1.0),    # High (#22C55E)
    4: (0.29, 0.87, 0.50, 1.0)     # Goal achieved (#4ADE80)
}

DAY_HEADERS = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]

class HeatmapWidget(Gtk.DrawingArea):
    def __init__(self, storage_manager):
        super().__init__()
        self.storage = storage_manager
        self.days_data = []

        self.set_content_width(380)
        self.set_content_height(175)
        self.set_hexpand(True)
        self.set_draw_func(self._on_draw)

        self.refresh()

    def refresh(self):
        self.days_data = self.storage.get_past_days_data()
        self.queue_draw()

    def _on_draw(self, area, cr: cairo.Context, width: int, height: int):
        cols = 7  # Mon - Sun
        rows = 4  # 4 Weeks
        gap = 8.0

        # Calculate cell size dynamically to fill the card nicely
        usable_w = width - 32.0
        cell_size = min(42.0, max(28.0, (usable_w - (cols - 1) * gap) / float(cols)))

        total_w = cols * cell_size + (cols - 1) * gap
        start_x = (width - total_w) / 2.0
        header_y = 6.0
        start_y = 30.0

        # 1. Draw Day-of-Week Column Headers (Pzt, Sal, Çar, Per, Cum, Cmt, Paz)
        header_layout = PangoCairo.create_layout(cr)
        font_desc = Pango.FontDescription("Ubuntu, Inter, Sans Bold 9")
        header_layout.set_font_description(font_desc)

        for c_idx in range(cols):
            x = start_x + c_idx * (cell_size + gap)
            header_layout.set_text(DAY_HEADERS[c_idx], -1)
            hw, hh = header_layout.get_pixel_size()

            cr.save()
            cr.set_source_rgba(0.58, 0.64, 0.72, 0.85)  # Slate-400
            cr.move_to(x + (cell_size - hw) / 2.0, header_y)
            PangoCairo.show_layout(cr, header_layout)
            cr.restore()

        if not self.days_data or len(self.days_data) < 28:
            return

        # 2. Draw 28 Day Cells
        num_layout = PangoCairo.create_layout(cr)
        num_font = Pango.FontDescription("Ubuntu, Inter, Sans Bold 9")
        num_layout.set_font_description(num_font)

        for idx, item in enumerate(self.days_data):
            r_idx = idx // cols
            c_idx = idx % cols

            x = start_x + c_idx * (cell_size + gap)
            y = start_y + r_idx * (cell_size + gap)

            lvl = item.get("level", 0)
            is_today = item.get("is_today", False)
            is_future = item.get("is_future", False)
            day_num = item.get("day_num", 1)

            # Draw cell rounded rectangle
            cr.save()
            r, g, b, a = LEVEL_COLORS.get(lvl, LEVEL_COLORS[0])
            cr.set_source_rgba(r, g, b, a)

            radius = 6.0
            cr.new_sub_path()
            cr.arc(x + cell_size - radius, y + radius, radius, -1.5708, 0)
            cr.arc(x + cell_size - radius, y + cell_size - radius, radius, 0, 1.5708)
            cr.arc(x + radius, y + cell_size - radius, radius, 1.5708, 3.1416)
            cr.arc(x + radius, y + radius, radius, 3.1416, 4.7124)
            cr.close_path()
            cr.fill_preserve()

            # Border styling
            if is_today:
                cr.set_source_rgba(0.98, 0.75, 0.14, 0.95)  # Bright Amber/Gold for today
                cr.set_line_width(2.2)
            elif is_future:
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.04)
                cr.set_line_width(1.0)
            else:
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.08)
                cr.set_line_width(1.0)
            cr.stroke()
            cr.restore()

            # Day Number Label
            num_layout.set_text(str(day_num), -1)
            nw, nh = num_layout.get_pixel_size()

            cr.save()
            if is_future:
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.2)
            elif lvl >= 2:
                cr.set_source_rgba(0.05, 0.12, 0.05, 0.95)  # Dark text on bright green
            elif is_today:
                cr.set_source_rgba(0.98, 0.75, 0.14, 1.0)
            else:
                cr.set_source_rgba(1.0, 1.0, 1.0, 0.6)

            cr.move_to(x + (cell_size - nw) / 2.0, y + (cell_size - nh) / 2.0)
            PangoCairo.show_layout(cr, num_layout)
            cr.restore()
