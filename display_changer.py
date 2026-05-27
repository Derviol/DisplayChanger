"""
DisplayChanger - Windows Display Resolution & Refresh Rate Changer
A modern tkinter GUI application for customizing display settings.

Uses Windows API via ctypes for display enumeration and modification.
Supports multi-monitor, common preset resolutions, and custom input.
"""

import ctypes
import ctypes.wintypes as wintypes
import tkinter as tk
from tkinter import ttk, messagebox
import sys
from dataclasses import dataclass, field

# ─── Windows API Constants ──────────────────────────────────────────────
ENUM_CURRENT_SETTINGS = -1
DM_PELSWIDTH = 0x00080000
DM_PELSHEIGHT = 0x00100000
DM_DISPLAYFREQUENCY = 0x00400000
DISPLAY_DEVICE_ACTIVE = 0x00000001
DISPLAY_DEVICE_ATTACHED_TO_DESKTOP = 0x00000004
DISPLAY_DEVICE_PRIMARY_DEVICE = 0x00000004
DISP_CHANGE_SUCCESSFUL = 0
DISP_CHANGE_RESTART = 1

# ─── Theme Colors ───────────────────────────────────────────────────────
class Theme:
    BG            = "#f5f6fa"
    CARD_BG       = "#ffffff"
    SIDEBAR_BG    = "#2c3e50"
    SIDEBAR_FG    = "#ecf0f1"
    ACCENT        = "#3498db"
    ACCENT_HOVER  = "#2980b9"
    ACCENT_PRESS  = "#21618c"
    DANGER        = "#e74c3c"
    DANGER_HOVER  = "#c0392b"
    SUCCESS       = "#27ae60"
    WARNING       = "#f39c12"
    TEXT_PRIMARY   = "#2c3e50"
    TEXT_SECONDARY = "#7f8c8d"
    TEXT_MUTED     = "#bdc3c7"
    BORDER        = "#dcdde1"
    SEPARATOR     = "#ebedef"
    HOVER_BG      = "#f0f3f7"
    SELECTED_BG   = "#ebf5fb"
    SELECTED_FG   = "#2980b9"
    BADGE_GREEN   = "#d5f5e3"
    BADGE_GREEN_FG= "#1e8449"
    BADGE_RED     = "#fadbd8"
    BADGE_RED_FG  = "#c0392b"
    INPUT_BG      = "#f8f9fa"
    INPUT_BORDER  = "#ced4da"
    INPUT_FOCUS   = "#3498db"

# ─── Common Resolutions ─────────────────────────────────────────────────
COMMON_RESOLUTIONS = [
    (640, 480, "640x480 (VGA)"),
    (800, 600, "800x600 (SVGA)"),
    (1024, 768, "1024x768 (XGA)"),
    (1152, 864, "1152x864"),
    (1280, 720, "1280x720 (HD 720p)"),
    (1280, 768, "1280x768"),
    (1280, 800, "1280x800 (WXGA)"),
    (1280, 960, "1280x960"),
    (1280, 1024, "1280x1024 (SXGA)"),
    (1360, 768, "1360x768"),
    (1366, 768, "1366x768"),
    (1400, 1050, "1400x1050 (SXGA+)"),
    (1440, 900, "1440x900 (WXGA+)"),
    (1440, 1080, "1440x1080"),
    (1536, 864, "1536x864"),
    (1600, 900, "1600x900 (HD+)"),
    (1600, 1024, "1600x1024"),
    (1600, 1200, "1600x1200 (UXGA)"),
    (1680, 1050, "1680x1050 (WSXGA+)"),
    (1920, 1080, "1920x1080 (Full HD)"),
    (1920, 1200, "1920x1200 (WUXGA)"),
    (1920, 1440, "1920x1440"),
    (2048, 1152, "2048x1152"),
    (2048, 1536, "2048x1536 (QXGA)"),
    (2560, 1080, "2560x1080 (UW-FHD)"),
    (2560, 1440, "2560x1440 (QHD)"),
    (2560, 1600, "2560x1600 (WQXGA)"),
    (2560, 2048, "2560x2048 (QSXGA)"),
    (3200, 1800, "3200x1800 (QHD+)"),
    (3440, 1440, "3440x1440 (UWQHD)"),
    (3840, 1600, "3840x1600 (UW4K)"),
    (3840, 2160, "3840x2160 (4K UHD)"),
    (3840, 2400, "3840x2400"),
    (4096, 2160, "4096x2160 (4K DCI)"),
    (5120, 2880, "5120x2880 (5K)"),
    (5120, 3200, "5120x3200"),
    (7680, 4320, "7680x4320 (8K UHD)"),
]


# ─── ctypes Structures ──────────────────────────────────────────────────

class DISPLAY_DEVICE(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("DeviceName", ctypes.c_wchar * 32),
        ("DeviceString", ctypes.c_wchar * 128),
        ("StateFlags", wintypes.DWORD),
        ("DeviceID", ctypes.c_wchar * 128),
        ("DeviceKey", ctypes.c_wchar * 128),
    ]


class DEVMODE(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", ctypes.c_wchar * 32),
        ("dmSpecVersion", wintypes.WORD),
        ("dmDriverVersion", wintypes.WORD),
        ("dmSize", wintypes.WORD),
        ("dmDriverExtra", wintypes.WORD),
        ("dmFields", wintypes.DWORD),
        ("dmPositionX", ctypes.c_long),
        ("dmPositionY", ctypes.c_long),
        ("dmDisplayOrientation", wintypes.DWORD),
        ("dmDisplayFixedOutput", wintypes.DWORD),
        ("dmColor", ctypes.c_short),
        ("dmDuplex", ctypes.c_short),
        ("dmYResolution", ctypes.c_short),
        ("dmTTOption", ctypes.c_short),
        ("dmCollate", ctypes.c_short),
        ("dmFormName", ctypes.c_wchar * 32),
        ("dmLogPixels", wintypes.WORD),
        ("dmBitsPerPel", wintypes.DWORD),
        ("dmPelsWidth", wintypes.DWORD),
        ("dmPelsHeight", wintypes.DWORD),
        ("dmDisplayFlags", wintypes.DWORD),
        ("dmDisplayFrequency", wintypes.DWORD),
        ("dmICMMethod", wintypes.DWORD),
        ("dmICMIntent", wintypes.DWORD),
        ("dmMediaType", wintypes.DWORD),
        ("dmDitherType", wintypes.DWORD),
        ("dmReserved1", wintypes.DWORD),
        ("dmReserved2", wintypes.DWORD),
        ("dmPanningWidth", wintypes.DWORD),
        ("dmPanningHeight", wintypes.DWORD),
    ]


# ─── Display Data Model ─────────────────────────────────────────────────

@dataclass
class DisplayInfo:
    name: str
    description: str
    is_primary: bool
    current_width: int
    current_height: int
    current_freq: int
    current_bpp: int
    supported_modes: list = field(default_factory=list)
    supported_resolutions: list = field(default_factory=list)
    supported_frequencies: dict = field(default_factory=dict)


# ─── Core Functions ─────────────────────────────────────────────────────

def enumerate_displays():
    displays = []
    user32 = ctypes.windll.user32
    i = 0
    while True:
        dd = DISPLAY_DEVICE()
        dd.cb = ctypes.sizeof(DISPLAY_DEVICE)
        if not user32.EnumDisplayDevicesW(None, i, ctypes.byref(dd), 0):
            break
        if not (dd.StateFlags & DISPLAY_DEVICE_ACTIVE):
            i += 1; continue
        if not (dd.StateFlags & DISPLAY_DEVICE_ATTACHED_TO_DESKTOP):
            i += 1; continue

        is_primary = bool(dd.StateFlags & DISPLAY_DEVICE_PRIMARY_DEVICE)
        dm_cur = DEVMODE()
        dm_cur.dmSize = ctypes.sizeof(DEVMODE)
        user32.EnumDisplaySettingsW(dd.DeviceName, ENUM_CURRENT_SETTINGS, ctypes.byref(dm_cur))

        info = DisplayInfo(
            name=dd.DeviceName, description=dd.DeviceString, is_primary=is_primary,
            current_width=dm_cur.dmPelsWidth, current_height=dm_cur.dmPelsHeight,
            current_freq=dm_cur.dmDisplayFrequency, current_bpp=dm_cur.dmBitsPerPel,
        )

        dm = DEVMODE()
        dm.dmSize = ctypes.sizeof(DEVMODE)
        j = 0
        res_set = set()
        freq_map = {}
        while user32.EnumDisplaySettingsW(dd.DeviceName, j, ctypes.byref(dm)):
            mode = DEVMODE()
            ctypes.memmove(ctypes.byref(mode), ctypes.byref(dm), ctypes.sizeof(DEVMODE))
            info.supported_modes.append(mode)
            key = (dm.dmPelsWidth, dm.dmPelsHeight)
            res_set.add(key)
            freq_map.setdefault(key, set()).add(dm.dmDisplayFrequency)
            j += 1
            dm.dmSize = ctypes.sizeof(DEVMODE)

        info.supported_resolutions = sorted(res_set)
        info.supported_frequencies = {k: sorted(v) for k, v in freq_map.items()}
        displays.append(info)
        i += 1
    return displays


def find_mode(display_info, width, height, frequency):
    for mode in display_info.supported_modes:
        if (mode.dmPelsWidth == width and mode.dmPelsHeight == height
                and mode.dmDisplayFrequency == frequency):
            return mode
    for mode in display_info.supported_modes:
        if mode.dmPelsWidth == width and mode.dmPelsHeight == height:
            return mode
    return None


def change_display_settings(display_info, width, height, frequency):
    user32 = ctypes.windll.user32
    mode = find_mode(display_info, width, height, frequency)
    if mode is None:
        return False, f"未找到匹配的显示模式: {width}x{height} @ {frequency} Hz"
    mode.dmFields = DM_PELSWIDTH | DM_PELSHEIGHT | DM_DISPLAYFREQUENCY
    result = user32.ChangeDisplaySettingsExW(
        display_info.name, ctypes.byref(mode), None, 0, None)
    if result == DISP_CHANGE_SUCCESSFUL:
        return True, "分辨率和刷新率已成功修改！"
    elif result == DISP_CHANGE_RESTART:
        return True, "设置已更改，需要重启生效。"
    elif result == -2:
        return False, "不支持的显示模式。"
    elif result == -3:
        return False, "无法写入注册表设置。"
    else:
        return False, f"修改失败 (错误码: {result})"


def revert_display_settings():
    ctypes.windll.user32.ChangeDisplaySettingsExW(None, None, None, 0, None)


# ═══════════════════════════════════════════════════════════════════════
#  Custom Widgets
# ═══════════════════════════════════════════════════════════════════════

class RoundedFrame(tk.Canvas):
    """A card with rounded corners drawn on a Canvas, containing a child frame."""

    def __init__(self, parent, radius=12, bg=Theme.CARD_BG, shadow=True, **kw):
        super().__init__(parent, highlightthickness=0, bg=parent["bg"], **kw)
        self._radius = radius
        self._bg = bg
        self._shadow = shadow
        self.bind("<Configure>", self._draw)
        self.inner = tk.Frame(self, bg=bg)
        self.create_window(0, 0, window=self.inner, anchor="nw",
                           tags="inner")

    def _draw(self, event=None):
        self.delete("bg")
        w, h = self.winfo_width(), self.winfo_height()
        r = self._radius
        if w < 2 or h < 2:
            return
        # Shadow
        if self._shadow:
            self._round_rect(3, 3, w, h, r, fill="#e8e8e8", outline="", tags="bg")
        # Card body
        self._round_rect(0, 0, w - 3, h - 3, r, fill=self._bg,
                         outline=Theme.BORDER, width=1, tags="bg")
        self.tag_lower("bg")
        # Resize inner frame
        self.coords("inner", (w - 3) // 2, (h - 3) // 2)
        self.itemconfigure("inner", width=w - 6, height=h - 6, anchor="center")

    def _round_rect(self, x1, y1, x2, y2, r, **kw):
        points = [
            x1 + r, y1, x2 - r, y1,
            x2, y1, x2, y1 + r,
            x2, y1 + r, x2, y2 - r,
            x2, y2, x2 - r, y2,
            x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r,
            x1, y2 - r, x1, y1 + r,
            x1, y1, x1 + r, y1,
        ]
        return self.create_polygon(points, smooth=True, **kw)


class FlatButton(tk.Canvas):
    """A flat button with rounded corners and hover / press effects."""

    def __init__(self, parent, text="Button", command=None,
                 bg=Theme.ACCENT, fg="#ffffff",
                 hover_bg=Theme.ACCENT_HOVER, press_bg=Theme.ACCENT_PRESS,
                 font=("Segoe UI", 10, "bold"), radius=8,
                 padx=18, pady=8, **kw):
        super().__init__(parent, highlightthickness=0, bg=parent["bg"],
                         cursor="hand2", **kw)
        self._text = text
        self._command = command
        self._bg = bg
        self._fg = fg
        self._hover_bg = hover_bg
        self._press_bg = press_bg
        self._font = font
        self._radius = radius
        self._padx = padx
        self._pady = pady
        self._state_bg = bg

        self.bind("<Configure>", self._draw)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def configure_text(self, text):
        self._text = text
        self._draw()

    def _draw(self, event=None):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        r = self._radius
        if w < 2 or h < 2:
            return
        self._round_rect(0, 0, w, h, r, fill=self._state_bg, outline="")
        self.create_text(w // 2, h // 2, text=self._text, fill=self._fg,
                         font=self._font, tags="label")

    def _round_rect(self, x1, y1, x2, y2, r, **kw):
        points = [
            x1 + r, y1, x2 - r, y1,
            x2, y1, x2, y1 + r,
            x2, y1 + r, x2, y2 - r,
            x2, y2, x2 - r, y2,
            x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r,
            x1, y2 - r, x1, y1 + r,
            x1, y1, x1 + r, y1,
        ]
        return self.create_polygon(points, smooth=True, **kw)

    def _on_enter(self, _):
        self._state_bg = self._hover_bg
        self._draw()

    def _on_leave(self, _):
        self._state_bg = self._bg
        self._draw()

    def _on_press(self, _):
        self._state_bg = self._press_bg
        self._draw()

    def _on_release(self, event):
        self._state_bg = self._hover_bg
        self._draw()
        if self._command:
            self._command()


class SegmentedControl(tk.Frame):
    """Two (or more) tab-like buttons side by side."""

    def __init__(self, parent, options, variable, command=None, **kw):
        super().__init__(parent, bg=Theme.CARD_BG, **kw)
        self._var = variable
        self._cmd = command
        self._btns = []
        for val, label in options:
            btn = tk.Label(self, text=label, font=("Segoe UI", 9),
                           bg=Theme.CARD_BG, fg=Theme.TEXT_SECONDARY,
                           padx=14, pady=6, cursor="hand2",
                           relief="flat", bd=0)
            btn.pack(side=tk.LEFT, padx=(0, 2))
            btn.bind("<Button-1>", lambda e, v=val: self._select(v))
            self._btns.append((val, btn))
        self._var.trace_add("write", lambda *_: self._refresh())
        self._refresh()

    def _select(self, val):
        self._var.set(val)
        if self._cmd:
            self._cmd()

    def _refresh(self):
        cur = self._var.get()
        for val, btn in self._btns:
            if val == cur:
                btn.configure(bg=Theme.ACCENT, fg="#ffffff",
                              font=("Segoe UI", 9, "bold"))
            else:
                btn.configure(bg=Theme.CARD_BG, fg=Theme.TEXT_SECONDARY,
                              font=("Segoe UI", 9))


class StyledEntry(tk.Frame):
    """Entry with border, focus highlight and placeholder."""

    def __init__(self, parent, placeholder="", width=12, **kw):
        super().__init__(parent, bg=Theme.INPUT_BORDER, **kw)
        self._inner = tk.Frame(self, bg=Theme.INPUT_BG, padx=1, pady=1)
        self._inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.var = tk.StringVar()
        self.entry = tk.Entry(self._inner, textvariable=self.var,
                              font=("Consolas", 11), width=width,
                              bg=Theme.INPUT_BG, fg=Theme.TEXT_PRIMARY,
                              relief="flat", bd=0, insertbackground=Theme.ACCENT)
        self.entry.pack(fill=tk.BOTH, expand=True, padx=4, pady=3)
        self._placeholder = placeholder
        self._show_placeholder()
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)

    def _show_placeholder(self):
        if not self.var.get():
            self.entry.configure(fg=Theme.TEXT_MUTED)
            self.entry.insert(0, self._placeholder)
            self._ph_active = True
        else:
            self._ph_active = False

    def _on_focus_in(self, _):
        self.configure(bg=Theme.INPUT_FOCUS)
        self._inner.configure(bg=Theme.INPUT_FOCUS)
        if self._ph_active:
            self.entry.delete(0, tk.END)
            self.entry.configure(fg=Theme.TEXT_PRIMARY)
            self._ph_active = False

    def _on_focus_out(self, _):
        self.configure(bg=Theme.INPUT_BORDER)
        self._inner.configure(bg=Theme.INPUT_BORDER)
        if not self.var.get():
            self._show_placeholder()

    def get_value(self):
        if self._ph_active:
            return ""
        return self.var.get().strip()


# ═══════════════════════════════════════════════════════════════════════
#  Main Application
# ═══════════════════════════════════════════════════════════════════════

class DisplayChangerApp:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DisplayChanger")
        self.root.geometry("860x780")
        self.root.minsize(800, 700)
        self.root.configure(bg=Theme.BG)

        # Windows dark title bar (best-effort, no-op on older OS)
        try:
            import ctypes as _ct
            hwnd = _ct.windll.user32.GetForegroundWindow()
            _ct.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 20, _ct.byref(_ct.c_int(0)), 4)
        except Exception:
            pass

        self.displays = []
        self.selected_display = None
        self._common_res_map = {}
        self._current_res_items = []  # (w, h, label, supported)

        self._detect_displays()
        self._build_ui()

        if self.displays:
            self._select_display(0)

    # ── detection ────────────────────────────────────────────────────────

    def _detect_displays(self):
        try:
            self.displays = enumerate_displays()
        except Exception as e:
            messagebox.showerror("错误", f"检测显示器失败:\n{e}")
            self.displays = []

    # ── UI construction ──────────────────────────────────────────────────

    def _build_ui(self):
        # Main layout: left content
        outer = tk.Frame(self.root, bg=Theme.BG)
        outer.pack(fill=tk.BOTH, expand=True)

        # Scrollable content area
        canvas = tk.Canvas(outer, bg=Theme.BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient=tk.VERTICAL, command=canvas.yview)
        self._scroll_frame = tk.Frame(canvas, bg=Theme.BG)

        self._scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._scroll_frame, anchor="nw",
                             tags="content")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Resize content window to fill canvas width
        def _on_canvas_configure(event):
            canvas.itemconfigure("content", width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        main = self._scroll_frame

        # ── Header ──
        header = tk.Frame(main, bg=Theme.ACCENT, height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        hdr_inner = tk.Frame(header, bg=Theme.ACCENT)
        hdr_inner.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(hdr_inner, text="DisplayChanger",
                 font=("Segoe UI", 22, "bold"),
                 bg=Theme.ACCENT, fg="#ffffff").pack(side=tk.LEFT)
        tk.Label(hdr_inner, text="  |  ",
                 font=("Segoe UI", 16), bg=Theme.ACCENT, fg="#a0cffc").pack(
                     side=tk.LEFT)
        tk.Label(hdr_inner, text="显示器分辨率 & 刷新率修改工具",
                 font=("Segoe UI", 11),
                 bg=Theme.ACCENT, fg="#d6eaf8").pack(side=tk.LEFT)

        # Content container with padding
        container = tk.Frame(main, bg=Theme.BG)
        container.pack(fill=tk.BOTH, expand=True, padx=28, pady=20)

        # ── Display selector card ──
        card1 = tk.Frame(container, bg=Theme.CARD_BG, highlightbackground=Theme.BORDER,
                         highlightthickness=1)
        card1.pack(fill=tk.X, pady=(0, 16))

        c1_top = tk.Frame(card1, bg=Theme.CARD_BG)
        c1_top.pack(fill=tk.X, padx=20, pady=(16, 0))
        self._section_label(c1_top, "选择显示器", "🖥").pack(anchor=tk.W)

        c1_body = tk.Frame(card1, bg=Theme.CARD_BG)
        c1_body.pack(fill=tk.X, padx=20, pady=(8, 16))

        self.display_combo = ttk.Combobox(c1_body, state="readonly",
                                           font=("Segoe UI", 10))
        names = []
        for d in self.displays:
            tag = " [主显示器]" if d.is_primary else ""
            names.append(f"{d.name} - {d.description}{tag}")
        self.display_combo["values"] = names
        self.display_combo.pack(fill=tk.X, pady=(0, 10))
        self.display_combo.bind("<<ComboboxSelected>>", self._on_display_selected)

        # Current info bar
        self._info_bar = tk.Frame(c1_body, bg=Theme.BG, padx=12, pady=10)
        self._info_bar.pack(fill=tk.X)
        self._info_res = tk.Label(self._info_bar, text="--",
                                  font=("Segoe UI", 18, "bold"),
                                  bg=Theme.BG, fg=Theme.ACCENT)
        self._info_res.pack(side=tk.LEFT)
        self._info_detail = tk.Label(self._info_bar, text="请选择显示器",
                                     font=("Segoe UI", 9),
                                     bg=Theme.BG, fg=Theme.TEXT_SECONDARY)
        self._info_detail.pack(side=tk.LEFT, padx=(16, 0))

        # ── Resolution card ──
        card2 = tk.Frame(container, bg=Theme.CARD_BG, highlightbackground=Theme.BORDER,
                         highlightthickness=1)
        card2.pack(fill=tk.X, pady=(0, 16))

        c2_top = tk.Frame(card2, bg=Theme.CARD_BG)
        c2_top.pack(fill=tk.X, padx=20, pady=(16, 0))
        self._section_label(c2_top, "设置分辨率", "").pack(anchor=tk.W, side=tk.LEFT)

        self.mode_var = tk.StringVar(value="preset")
        seg = SegmentedControl(c2_top, [("preset", "常用分辨率"),
                                         ("custom", "自定义输入")],
                               self.mode_var, command=self._on_mode_changed)
        seg.pack(side=tk.RIGHT)

        c2_body = tk.Frame(card2, bg=Theme.CARD_BG)
        c2_body.pack(fill=tk.X, padx=20, pady=(10, 16))

        # Preset sub-frame
        self.preset_frame = tk.Frame(c2_body, bg=Theme.CARD_BG)
        self.preset_frame.pack(fill=tk.X)

        # Search / filter row
        filter_row = tk.Frame(self.preset_frame, bg=Theme.CARD_BG)
        filter_row.pack(fill=tk.X, pady=(0, 6))
        tk.Label(filter_row, text="搜索:", font=("Segoe UI", 9),
                 bg=Theme.CARD_BG, fg=Theme.TEXT_SECONDARY).pack(side=tk.LEFT)
        self._filter_var = tk.StringVar()
        self._filter_var.trace_add("write", lambda *_: self._apply_filter())
        filter_entry = tk.Entry(filter_row, textvariable=self._filter_var,
                                font=("Segoe UI", 9), width=20,
                                bg=Theme.INPUT_BG, fg=Theme.TEXT_PRIMARY,
                                relief="flat", bd=1,
                                insertbackground=Theme.ACCENT)
        filter_entry.pack(side=tk.LEFT, padx=(6, 0))

        # Resolution listbox
        list_frame = tk.Frame(self.preset_frame, bg=Theme.BORDER)
        list_frame.pack(fill=tk.X)
        self.res_listbox = tk.Listbox(
            list_frame, font=("Segoe UI", 10), height=7,
            bg=Theme.CARD_BG, fg=Theme.TEXT_PRIMARY,
            selectbackground=Theme.ACCENT, selectforeground="#ffffff",
            selectmode=tk.SINGLE, relief="flat", bd=0,
            activestyle="none", highlightthickness=0,
            exportselection=False)
        res_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                    command=self.res_listbox.yview)
        self.res_listbox.configure(yscrollcommand=res_scroll.set)
        self.res_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        res_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.res_listbox.bind("<<ListboxSelect>>", self._on_resolution_selected)

        self._res_hint = tk.Label(self.preset_frame, text="",
                                  font=("Segoe UI", 8),
                                  bg=Theme.CARD_BG, fg=Theme.TEXT_MUTED)
        self._res_hint.pack(anchor=tk.W, pady=(4, 0))

        # Custom sub-frame (hidden initially)
        self.custom_frame = tk.Frame(c2_body, bg=Theme.CARD_BG)

        cf_row = tk.Frame(self.custom_frame, bg=Theme.CARD_BG)
        cf_row.pack(fill=tk.X, pady=(0, 8))

        tk.Label(cf_row, text="宽度", font=("Segoe UI", 9),
                 bg=Theme.CARD_BG, fg=Theme.TEXT_SECONDARY).pack(side=tk.LEFT)
        self.width_entry = StyledEntry(cf_row, placeholder="例如 1920", width=12)
        self.width_entry.pack(side=tk.LEFT, padx=(8, 20))
        self.width_entry.entry.bind("<FocusOut>", self._on_custom_res_changed)
        self.width_entry.entry.bind("<Return>", self._on_custom_res_changed)

        tk.Label(cf_row, text="高度", font=("Segoe UI", 9),
                 bg=Theme.CARD_BG, fg=Theme.TEXT_SECONDARY).pack(side=tk.LEFT)
        self.height_entry = StyledEntry(cf_row, placeholder="例如 1080", width=12)
        self.height_entry.pack(side=tk.LEFT, padx=(8, 0))
        self.height_entry.entry.bind("<FocusOut>", self._on_custom_res_changed)
        self.height_entry.entry.bind("<Return>", self._on_custom_res_changed)

        tk.Label(self.custom_frame,
                 text="输入的分辨率必须是显示器已支持的模式",
                 font=("Segoe UI", 8), bg=Theme.CARD_BG,
                 fg=Theme.WARNING).pack(anchor=tk.W)

        # ── Refresh rate card ──
        card3 = tk.Frame(container, bg=Theme.CARD_BG, highlightbackground=Theme.BORDER,
                         highlightthickness=1)
        card3.pack(fill=tk.X, pady=(0, 16))

        c3_top = tk.Frame(card3, bg=Theme.CARD_BG)
        c3_top.pack(fill=tk.X, padx=20, pady=(16, 0))
        self._section_label(c3_top, "设置刷新率", "").pack(anchor=tk.W, side=tk.LEFT)

        self._freq_badge = tk.Label(c3_top, text="", font=("Segoe UI", 9),
                                     bg=Theme.BADGE_GREEN, fg=Theme.BADGE_GREEN_FG,
                                     padx=8, pady=2)
        self._freq_badge.pack(side=tk.RIGHT)

        c3_body = tk.Frame(card3, bg=Theme.CARD_BG)
        c3_body.pack(fill=tk.X, padx=20, pady=(10, 16))

        freq_inner = tk.Frame(c3_body, bg=Theme.CARD_BG)
        freq_inner.pack(fill=tk.X)

        tk.Label(freq_inner, text="刷新率 (Hz)",
                 font=("Segoe UI", 9),
                 bg=Theme.CARD_BG, fg=Theme.TEXT_SECONDARY).pack(side=tk.LEFT)

        self.freq_combo = ttk.Combobox(freq_inner, state="readonly",
                                        font=("Segoe UI", 11), width=12)
        self.freq_combo.pack(side=tk.LEFT, padx=(12, 0))

        self._freq_info = tk.Label(c3_body, text="选择分辨率后显示可用刷新率",
                                    font=("Segoe UI", 8),
                                    bg=Theme.CARD_BG, fg=Theme.TEXT_MUTED)
        self._freq_info.pack(anchor=tk.W, pady=(6, 0))

        # ── Action buttons ──
        btn_bar = tk.Frame(container, bg=Theme.BG)
        btn_bar.pack(fill=tk.X, pady=(4, 8))

        self._apply_btn = FlatButton(
            btn_bar, text="  应用设置  ", command=self._apply,
            bg=Theme.ACCENT, hover_bg=Theme.ACCENT_HOVER,
            press_bg=Theme.ACCENT_PRESS, font=("Segoe UI", 11, "bold"),
            padx=24, pady=10)
        self._apply_btn.pack(side=tk.LEFT, padx=(0, 12))
        self._apply_btn.configure(width=140, height=40)

        self._revert_btn = FlatButton(
            btn_bar, text="恢复默认", command=self._revert,
            bg=Theme.DANGER, hover_bg=Theme.DANGER_HOVER,
            press_bg="#a93226", font=("Segoe UI", 10),
            padx=18, pady=10)
        self._revert_btn.pack(side=tk.LEFT, padx=(0, 12))
        self._revert_btn.configure(width=110, height=40)

        self._refresh_btn = FlatButton(
            btn_bar, text="重新检测", command=self._refresh_displays,
            bg=Theme.TEXT_SECONDARY, hover_bg=Theme.TEXT_PRIMARY,
            press_bg="#1a252f", font=("Segoe UI", 10),
            padx=18, pady=10)
        self._refresh_btn.pack(side=tk.LEFT)
        self._refresh_btn.configure(width=110, height=40)

        # ── Status bar ──
        status_bar = tk.Frame(container, bg=Theme.BG)
        status_bar.pack(fill=tk.X, pady=(8, 0))
        self._status_dot = tk.Canvas(status_bar, width=8, height=8,
                                      bg=Theme.BG, highlightthickness=0)
        self._status_dot.pack(side=tk.LEFT, padx=(0, 6))
        self._draw_status_dot(Theme.SUCCESS)
        self.status_var = tk.StringVar(value="就绪")
        tk.Label(status_bar, textvariable=self.status_var,
                 font=("Segoe UI", 9), bg=Theme.BG,
                 fg=Theme.TEXT_MUTED).pack(side=tk.LEFT)

    # ── widget helpers ───────────────────────────────────────────────────

    def _section_label(self, parent, text, icon):
        frame = tk.Frame(parent, bg=Theme.CARD_BG)
        if icon:
            tk.Label(frame, text=icon, font=("Segoe UI", 14),
                     bg=Theme.CARD_BG).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(frame, text=text, font=("Segoe UI", 11, "bold"),
                 bg=Theme.CARD_BG, fg=Theme.TEXT_PRIMARY).pack(side=tk.LEFT)
        return frame

    def _draw_status_dot(self, color):
        self._status_dot.delete("all")
        self._status_dot.create_oval(2, 2, 8, 8, fill=color, outline="")

    # ── display logic ────────────────────────────────────────────────────

    def _select_display(self, idx):
        if idx < 0 or idx >= len(self.displays):
            return
        self.display_combo.current(idx)
        self._on_display_selected(None)

    def _on_display_selected(self, _event):
        sel = self.display_combo.current()
        if sel < 0 or sel >= len(self.displays):
            return
        self.selected_display = self.displays[sel]
        d = self.selected_display
        self._info_res.configure(text=f"{d.current_width}x{d.current_height}")
        self._info_detail.configure(
            text=f"@ {d.current_freq} Hz    "
                 f"{d.current_bpp} bit    "
                 f"{len(d.supported_modes)} 种模式")
        self._update_res_list()
        self._update_freq_list()
        self.status_var.set(f"已选择 {d.name}")
        self._draw_status_dot(Theme.SUCCESS)

    # ── resolution list ──────────────────────────────────────────────────

    def _build_res_items(self):
        """Build the full resolution item list for the current display."""
        if not self.selected_display:
            self._current_res_items = []
            return
        d = self.selected_display
        items = []
        for idx, (w, h, label) in enumerate(COMMON_RESOLUTIONS):
            sup = (w, h) in d.supported_resolutions
            items.append((w, h, label, sup))
        self._current_res_items = items

    def _update_res_list(self):
        self._build_res_items()
        self._apply_filter()

    def _apply_filter(self):
        self.res_listbox.delete(0, tk.END)
        self._common_res_map = {}
        filt = self._filter_var.get().lower().strip()
        lb_idx = 0
        for w, h, label, sup in self._current_res_items:
            if filt and filt not in label.lower() and filt not in f"{w}x{h}":
                continue
            tag = "✓" if sup else "✗"
            display = f"  {tag}  {label}"
            self.res_listbox.insert(tk.END, display)
            self._common_res_map[lb_idx] = (w, h)
            # Color-code the row
            if sup:
                self.res_listbox.itemconfig(lb_idx,
                    fg=Theme.TEXT_PRIMARY, selectforeground="#ffffff")
            else:
                self.res_listbox.itemconfig(lb_idx,
                    fg=Theme.TEXT_MUTED, selectforeground="#ffffff")
            lb_idx += 1
        total = len(self._current_res_items)
        sup_count = sum(1 for _, _, _, s in self._current_res_items if s)
        self._res_hint.configure(
            text=f"共 {total} 种常用分辨率，当前显示器支持 {sup_count} 种")

    def _on_resolution_selected(self, _event):
        self._update_freq_list()

    def _on_mode_changed(self):
        if self.mode_var.get() == "preset":
            self.custom_frame.pack_forget()
            self.preset_frame.pack(fill=tk.X)
        else:
            self.preset_frame.pack_forget()
            self.custom_frame.pack(fill=tk.X)

    def _on_custom_res_changed(self, _event=None):
        if self.mode_var.get() == "custom" and self.selected_display:
            self._update_freq_list()

    # ── frequency ────────────────────────────────────────────────────────

    def _get_selected_resolution(self):
        if self.mode_var.get() == "preset":
            sel = self.res_listbox.curselection()
            if not sel:
                return None, None
            idx = sel[0]
            if idx not in self._common_res_map:
                return None, None
            return self._common_res_map[idx]
        try:
            w = int(self.width_entry.get_value())
            h = int(self.height_entry.get_value())
            return (w, h) if w > 0 and h > 0 else (None, None)
        except (ValueError, TypeError):
            return None, None

    def _update_freq_list(self):
        if not self.selected_display:
            return
        d = self.selected_display
        w, h = self._get_selected_resolution()
        if not w or not h:
            self.freq_combo["values"] = []
            self._freq_info.configure(text="请选择分辨率")
            self._freq_badge.configure(text="", bg=Theme.CARD_BG)
            return
        key = (w, h)
        if key in d.supported_frequencies:
            freqs = d.supported_frequencies[key]
            self.freq_combo["values"] = [f"{f} Hz" for f in freqs]
            self.freq_combo.current(len(freqs) - 1)
            self._freq_info.configure(
                text=f"该分辨率支持 {len(freqs)} 种刷新率")
            self._freq_badge.configure(
                text=f"  已支持  ",
                bg=Theme.BADGE_GREEN, fg=Theme.BADGE_GREEN_FG)
        else:
            self.freq_combo["values"] = []
            self._freq_info.configure(text="该分辨率不受此显示器支持")
            self._freq_badge.configure(
                text=f"  不支持  ",
                bg=Theme.BADGE_RED, fg=Theme.BADGE_RED_FG)

    # ── apply / revert ───────────────────────────────────────────────────

    def _apply(self):
        if not self.selected_display:
            messagebox.showwarning("提示", "请先选择一个显示器。")
            return

        d = self.selected_display
        w, h = self._get_selected_resolution()
        if not w or not h:
            messagebox.showwarning("提示", "请选择或输入有效的分辨率。")
            return

        ft = self.freq_combo.get()
        if ft:
            freq = int(ft.replace(" Hz", ""))
        elif self.mode_var.get() == "custom":
            key = (w, h)
            if key in d.supported_frequencies:
                freq = d.supported_frequencies[key][-1]
            else:
                messagebox.showwarning(
                    "提示", f"分辨率 {w}x{h} 不受显示器 {d.name} 支持。")
                return
        else:
            messagebox.showwarning("提示", "请选择刷新率。")
            return

        key = (w, h)
        if key not in d.supported_resolutions:
            messagebox.showwarning(
                "提示", f"分辨率 {w}x{h} 不受显示器 {d.name} 支持。")
            return
        if freq not in d.supported_frequencies.get(key, []):
            messagebox.showwarning(
                "提示", f"刷新率 {freq} Hz 在 {w}x{h} 下不受支持。")
            return

        if not messagebox.askyesno(
                "确认修改",
                f"即将修改显示器设置:\n\n"
                f"  显示器 : {d.name}\n"
                f"  分辨率 : {w}x{h}\n"
                f"  刷新率 : {freq} Hz\n\n"
                f"  当前   : {d.current_width}x{d.current_height}"
                f" @ {d.current_freq} Hz\n\n"
                f"确认修改？"):
            return

        self.status_var.set("正在应用设置...")
        self._draw_status_dot(Theme.WARNING)
        self.root.update()

        ok, msg = change_display_settings(d, w, h, freq)
        if ok:
            messagebox.showinfo(
                "成功", msg + "\n\n如显示异常，请点击「恢复默认」。")
            self.status_var.set("设置已应用")
            self._draw_status_dot(Theme.SUCCESS)
            self._refresh_current_info()
        else:
            messagebox.showerror("失败", msg)
            self.status_var.set("设置应用失败")
            self._draw_status_dot(Theme.DANGER)

    def _revert(self):
        if messagebox.askyesno("恢复设置", "确认恢复所有显示器到原始设置？"):
            revert_display_settings()
            self.status_var.set("已恢复默认设置")
            self._draw_status_dot(Theme.SUCCESS)
            self._refresh_current_info()
            messagebox.showinfo("完成", "显示器设置已恢复。")

    def _refresh_displays(self):
        self.status_var.set("正在重新检测显示器...")
        self._draw_status_dot(Theme.WARNING)
        self.root.update()
        self._detect_displays()
        names = []
        for d in self.displays:
            tag = " [主显示器]" if d.is_primary else ""
            names.append(f"{d.name} - {d.description}{tag}")
        self.display_combo["values"] = names
        if self.displays:
            self._select_display(0)
        self.status_var.set(f"检测到 {len(self.displays)} 个显示器")
        self._draw_status_dot(Theme.SUCCESS)

    def _refresh_current_info(self):
        if not self.selected_display:
            return
        self._detect_displays()
        idx = self.display_combo.current()
        if 0 <= idx < len(self.displays):
            self.selected_display = self.displays[idx]
            d = self.selected_display
            self._info_res.configure(text=f"{d.current_width}x{d.current_height}")
            self._info_detail.configure(
                text=f"@ {d.current_freq} Hz    "
                     f"{d.current_bpp} bit    "
                     f"{len(d.supported_modes)} 种模式")
            self._update_res_list()
            self._update_freq_list()

    def run(self):
        self.root.mainloop()


# ─── Entry Point ────────────────────────────────────────────────────────

def main():
    if sys.platform != "win32":
        print("此程序仅支持 Windows 系统。")
        sys.exit(1)
    DisplayChangerApp().run()


if __name__ == "__main__":
    main()
