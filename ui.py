import os, json, time, math, random, threading
import tkinter as tk
from collections import deque
from PIL import Image, ImageTk, ImageDraw
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key

load_dotenv()


def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


BASE_DIR   = get_base_dir()
CONFIG_DIR = BASE_DIR / "config"
ENV_FILE   = BASE_DIR / ".env"

SYSTEM_NAME = "J.A.R.V.I.S"
MODEL_BADGE = "Mark II"
SUBTITLE    = "Just A Rather Very Intelligent System"

# ── Marvel JARVIS Colour Palette ──────────────────────────────────────────────
C_BG      = "#010810"   # near-black navy
C_PRI     = "#00c8ff"   # holographic cyan
C_GOLD    = "#e8a020"   # arc-reactor gold
C_GOLD2   = "#ffcc44"   # bright gold accent
C_MID     = "#0077aa"   # mid blue
C_DIM     = "#003355"   # dim blue
C_DIMMER  = "#000d1a"   # very deep
C_TEXT    = "#8fffff"   # light cyan text
C_PANEL   = "#00090f"   # panel bg
C_GREEN   = "#00ff88"
C_RED     = "#ff3333"
C_WHITE   = "#d0eeff"


class JarvisUI:

    def __init__(self, face_path, size=None):
        self.root = tk.Tk()
        self.root.title(f"{SYSTEM_NAME} — {MODEL_BADGE}")
        self.root.resizable(False, False)

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        W  = min(sw, 1100)
        H  = min(sh, 840)
        self.root.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")
        self.root.configure(bg=C_BG)

        self.W = W
        self.H = H

        self.FACE_SZ = min(int(H * 0.46), 360)
        self.FCX     = W // 2
        self.FCY     = int(H * 0.14) + self.FACE_SZ // 2

        # animation state
        self.speaking      = False
        self.scale         = 1.0
        self.target_scale  = 1.0
        self.halo_a        = 70.0
        self.target_halo   = 70.0
        self.last_t        = time.time()
        self.tick          = 0
        self.scan_angle    = 0.0
        self.scan2_angle   = 180.0
        self.rings_spin    = [0.0, 60.0, 120.0, 240.0]
        self.pulse_r       = [0.0, self.FACE_SZ * 0.3, self.FACE_SZ * 0.6]
        self.hex_offset    = 0.0
        self.status_text   = "INITIALISING"
        self.status_blink  = True
        self.data_tick     = 0

        # fake side-panel data streams
        self._data_left  = ["0.000"] * 8
        self._data_right = ["0.000"] * 8

        self.typing_queue = deque()
        self.is_typing    = False

        self._face_pil         = None
        self._has_face         = False
        self._face_scale_cache = None
        self._load_face(face_path)

        self.bg = tk.Canvas(self.root, width=W, height=H,
                            bg=C_BG, highlightthickness=0)
        self.bg.place(x=0, y=0)

        # log panel
        LW = int(W * 0.56)
        LH = 130
        self.log_frame = tk.Frame(self.root, bg=C_PANEL,
                                  highlightbackground=C_MID,
                                  highlightthickness=1)
        self.log_frame.place(x=(W - LW) // 2, y=H - LH - 32, width=LW, height=LH)
        self.log_text = tk.Text(
            self.log_frame, fg=C_TEXT, bg=C_PANEL,
            insertbackground=C_TEXT, borderwidth=0,
            wrap="word", font=("Courier", 10), padx=10, pady=6
        )
        self.log_text.pack(fill="both", expand=True)
        self.log_text.configure(state="disabled")
        self.log_text.tag_config("you",  foreground="#d0eeff")
        self.log_text.tag_config("ai",   foreground=C_PRI)
        self.log_text.tag_config("sys",  foreground=C_GOLD2)

        self._api_key_ready = self._api_keys_exist()
        if not self._api_key_ready:
            self._show_setup_ui()

        self._animate()
        self.root.protocol("WM_DELETE_WINDOW", lambda: os._exit(0))

    # ── helpers ──────────────────────────────────────────────────────────────

    def _load_face(self, path):
        FW = self.FACE_SZ
        try:
            img  = Image.open(path).convert("RGBA").resize((FW, FW), Image.LANCZOS)
            mask = Image.new("L", (FW, FW), 0)
            ImageDraw.Draw(mask).ellipse((2, 2, FW - 2, FW - 2), fill=255)
            img.putalpha(mask)
            self._face_pil = img
            self._has_face = True
        except Exception:
            self._has_face = False

    @staticmethod
    def _ac(r, g, b, a):
        f = a / 255.0
        return f"#{int(r*f):02x}{int(g*f):02x}{int(b*f):02x}"

    def _hex_color(self, a):
        return self._ac(0, 200, 255, a)

    # ── animation loop ────────────────────────────────────────────────────────

    def _animate(self):
        self.tick     += 1
        self.data_tick += 1
        t   = self.tick
        now = time.time()

        # update targets
        if now - self.last_t > (0.12 if self.speaking else 0.5):
            if self.speaking:
                self.target_scale = random.uniform(1.04, 1.10)
                self.target_halo  = random.uniform(150, 200)
            else:
                self.target_scale = random.uniform(1.001, 1.006)
                self.target_halo  = random.uniform(55, 80)
            self.last_t = now

        sp = 0.32 if self.speaking else 0.14
        self.scale  += (self.target_scale - self.scale) * sp
        self.halo_a += (self.target_halo  - self.halo_a) * sp

        speeds = [1.4, -0.9, 2.1, -1.5] if self.speaking else [0.55, -0.32, 0.9, -0.6]
        for i, spd in enumerate(speeds):
            self.rings_spin[i] = (self.rings_spin[i] + spd) % 360

        self.scan_angle  = (self.scan_angle  + (3.0 if self.speaking else 1.4)) % 360
        self.scan2_angle = (self.scan2_angle + (-2.0 if self.speaking else -0.9)) % 360
        self.hex_offset  = (self.hex_offset  + 0.3) % 40

        pspd  = 4.0 if self.speaking else 1.8
        limit = self.FACE_SZ * 0.76
        new_p = [r + pspd for r in self.pulse_r if r + pspd < limit]
        if len(new_p) < 4 and random.random() < (0.07 if self.speaking else 0.025):
            new_p.append(0.0)
        self.pulse_r = new_p

        if t % 38 == 0:
            self.status_blink = not self.status_blink

        # refresh fake data panels every 12 frames
        if self.data_tick % 12 == 0:
            self._data_left  = [f"{random.uniform(0,999):.3f}" for _ in range(8)]
            self._data_right = [f"{random.uniform(0,999):.3f}" for _ in range(8)]

        self._draw()
        self.root.after(16, self._animate)

    # ── draw ──────────────────────────────────────────────────────────────────

    def _draw(self):
        c    = self.bg
        W, H = self.W, self.H
        t    = self.tick
        FCX  = self.FCX
        FCY  = self.FCY
        FW   = self.FACE_SZ
        
        if not hasattr(self, '_static_drawn'):
            self._draw_hex_grid(c, W, H)
            self._static_drawn = True

        c.delete("dynamic")
        
        class DynC:
            def __getattr__(self, name):
                if name.startswith("create_"):
                    def proxy(*args, **kwargs):
                        kwargs["tags"] = kwargs.get("tags", "") + " dynamic"
                        return getattr(c, name)(*args, **kwargs)
                    return proxy
                return getattr(c, name)
        
        dyn_c = DynC()

        self._draw_glow_bg(dyn_c, FCX, FCY, FW)
        self._draw_pulse_rings(dyn_c, FCX, FCY, FW)
        self._draw_orbital_rings(dyn_c, FCX, FCY, FW)
        self._draw_scan_arcs(dyn_c, FCX, FCY, FW)
        self._draw_tick_marks(dyn_c, FCX, FCY, FW)
        self._draw_crosshairs(dyn_c, FCX, FCY, FW)
        self._draw_corner_brackets(dyn_c, FCX, FCY, FW)
        self._draw_face_or_orb(dyn_c, FCX, FCY, FW)
        self._draw_arc_reactor_core(dyn_c, FCX, FCY, FW)
        self._draw_header(dyn_c, W, H)
        self._draw_status(dyn_c, W, FCY, FW, t)
        self._draw_side_panels(dyn_c, W, H, FCX, FCY, FW)
        self._draw_footer(dyn_c, W, H)

    def _draw_hex_grid(self, c, W, H):
        """Honeycomb hex grid background."""
        R  = 22
        dx = R * 2
        dy = int(R * 1.73)
        for row in range(-1, H // dy + 2):
            for col in range(-1, W // dx + 2):
                ox = (row % 2) * R
                x  = col * dx + ox + (int(self.hex_offset) % dx)
                y  = row * dy
                pts = []
                for i in range(6):
                    a = math.radians(60 * i - 30)
                    pts.extend([x + R * 0.95 * math.cos(a),
                                 y + R * 0.95 * math.sin(a)])
                c.create_polygon(pts, outline="#001a2e", fill="", width=1)

    def _draw_glow_bg(self, c, FCX, FCY, FW):
        for r in range(int(FW * 0.60), int(FW * 0.25), -18):
            frac = 1.0 - (r - FW * 0.25) / (FW * 0.35)
            ga   = max(0, min(255, int(self.halo_a * 0.11 * frac)))
            c.create_oval(FCX-r, FCY-r, FCX+r, FCY+r,
                          outline=self._ac(0, 140, 220, ga), width=2)

    def _draw_pulse_rings(self, c, FCX, FCY, FW):
        for pr in self.pulse_r:
            pa = max(0, int(240 * (1.0 - pr / (FW * 0.76))))
            r  = int(pr)
            c.create_oval(FCX-r, FCY-r, FCX+r, FCY+r,
                          outline=self._ac(0, 200, 255, pa), width=2)

    def _draw_orbital_rings(self, c, FCX, FCY, FW):
        configs = [
            (0.50, 3, 100, 80,  C_PRI),
            (0.42, 2, 72,  60,  C_MID),
            (0.34, 2, 55,  45,  C_PRI),
            (0.26, 1, 40,  35,  C_GOLD),
        ]
        for idx, (r_frac, w_ring, arc_l, gap, base_col) in enumerate(configs):
            ring_r = int(FW * r_frac)
            base_a = self.rings_spin[idx]
            a_val  = max(0, min(255, int(self.halo_a * (1.0 - idx * 0.15))))
            # parse base_col hex to rgb
            r, g, b = (int(base_col[1:3],16), int(base_col[3:5],16), int(base_col[5:7],16))
            col = self._ac(r, g, b, a_val)
            segments = 360 // (arc_l + gap)
            for s in range(segments):
                start = (base_a + s * (arc_l + gap)) % 360
                c.create_arc(FCX-ring_r, FCY-ring_r, FCX+ring_r, FCY+ring_r,
                             start=start, extent=arc_l,
                             outline=col, width=w_ring, style="arc")

    def _draw_scan_arcs(self, c, FCX, FCY, FW):
        sr      = int(FW * 0.52)
        scan_a  = min(255, int(self.halo_a * 1.5))
        arc_ext = 80 if self.speaking else 48
        c.create_arc(FCX-sr, FCY-sr, FCX+sr, FCY+sr,
                     start=self.scan_angle, extent=arc_ext,
                     outline=self._ac(0, 200, 255, scan_a), width=3, style="arc")
        c.create_arc(FCX-sr, FCY-sr, FCX+sr, FCY+sr,
                     start=self.scan2_angle, extent=arc_ext // 2,
                     outline=self._ac(232, 160, 32, scan_a // 2), width=2, style="arc")

    def _draw_tick_marks(self, c, FCX, FCY, FW):
        t_out = int(FW * 0.515)
        t_in  = int(FW * 0.490)
        a_mk  = self._ac(0, 200, 255, 140)
        for deg in range(0, 360, 6):
            rad = math.radians(deg)
            inn = t_in - 4 if deg % 30 == 0 else t_in
            c.create_line(FCX + t_out * math.cos(rad), FCY - t_out * math.sin(rad),
                          FCX + inn  * math.cos(rad), FCY - inn  * math.sin(rad),
                          fill=a_mk, width=(2 if deg % 30 == 0 else 1))

    def _draw_crosshairs(self, c, FCX, FCY, FW):
        ch_r = int(FW * 0.53)
        gap  = int(FW * 0.14)
        ch_a = self._ac(0, 200, 255, int(self.halo_a * 0.45))
        for x1, y1, x2, y2 in [
                (FCX - ch_r, FCY, FCX - gap, FCY), (FCX + gap, FCY, FCX + ch_r, FCY),
                (FCX, FCY - ch_r, FCX, FCY - gap), (FCX, FCY + gap, FCX, FCY + ch_r)]:
            c.create_line(x1, y1, x2, y2, fill=ch_a, width=1)

    def _draw_corner_brackets(self, c, FCX, FCY, FW):
        """Iron Man HUD-style corner brackets around the face circle."""
        blen = 28
        boff = int(FW * 0.52)
        bc   = self._ac(232, 160, 32, 210)
        bc2  = self._ac(0, 200, 255, 180)
        for ang_deg in [45, 135, 225, 315]:
            rad = math.radians(ang_deg)
            cx  = FCX + boff * math.cos(rad)
            cy  = FCY - boff * math.sin(rad)
            # two bracket lines perpendicular to radius
            t1r = math.radians(ang_deg + 90)
            t2r = math.radians(ang_deg - 90)
            c.create_line(cx, cy,
                          cx + blen * math.cos(rad),  cy - blen * math.sin(rad),
                          fill=bc2, width=2)
            c.create_line(cx, cy,
                          cx + blen * math.cos(t1r), cy - blen * math.sin(t1r),
                          fill=bc, width=2)

    def _draw_face_or_orb(self, c, FCX, FCY, FW):
        if self._has_face:
            fw = int(FW * self.scale)
            if (self._face_scale_cache is None or
                    abs(self._face_scale_cache[0] - self.scale) > 0.004):
                scaled = self._face_pil.resize((fw, fw), Image.BILINEAR)
                tk_img = ImageTk.PhotoImage(scaled)
                self._face_scale_cache = (self.scale, tk_img)
            c.create_image(FCX, FCY, image=self._face_scale_cache[1])
        else:
            # glowing orb with nested rings
            orb_r = int(FW * 0.24 * self.scale)
            for i in range(8, 0, -1):
                r2   = int(orb_r * i / 8)
                frac = i / 8
                ga   = max(0, min(255, int(self.halo_a * 1.2 * frac)))
                c.create_oval(FCX-r2, FCY-r2, FCX+r2, FCY+r2,
                              fill=self._ac(0, int(50*frac), int(100*frac), ga),
                              outline="")
            c.create_text(FCX, FCY, text=SYSTEM_NAME,
                          fill=self._ac(0, 200, 255, min(255, int(self.halo_a * 2.2))),
                          font=("Courier", 13, "bold"))

    def _draw_arc_reactor_core(self, c, FCX, FCY, FW):
        """Small arc-reactor style inner core ring."""
        cr = int(FW * 0.12)
        ca = min(255, int(self.halo_a * 1.8))
        # outer glow ring
        c.create_oval(FCX-cr, FCY-cr, FCX+cr, FCY+cr,
                      outline=self._ac(0, 200, 255, ca), width=2)
        # inner dot
        ir = int(FW * 0.055)
        c.create_oval(FCX-ir, FCY-ir, FCX+ir, FCY+ir,
                      fill=self._ac(0, 160, 220, int(ca * 0.6)), outline="")

    def _draw_header(self, c, W, H):
        HDR = 58
        c.create_rectangle(0, 0, W, HDR, fill="#00060e", outline="")
        # gold accent line
        c.create_line(0, HDR, W, HDR, fill=C_GOLD, width=2)
        c.create_line(0, HDR - 2, W, HDR - 2, fill=C_DIM, width=1)

        # Title
        c.create_text(W // 2, 20, text=SYSTEM_NAME,
                      fill=C_PRI, font=("Courier", 20, "bold"))
        c.create_text(W // 2, 42, text=SUBTITLE,
                      fill=C_MID, font=("Courier", 9))

        # left badge
        c.create_text(18, 29, text=MODEL_BADGE,
                      fill=C_GOLD, font=("Courier", 10, "bold"), anchor="w")
        # right clock
        c.create_text(W - 16, 29, text=time.strftime("%H:%M:%S"),
                      fill=C_PRI, font=("Courier", 14, "bold"), anchor="e")

        # header corner decorations
        for x, anchor in [(0, "nw"), (W, "ne")]:
            pass

    def _draw_status(self, c, W, FCY, FW, t):
        sy = FCY + FW // 2 + 38
        if self.speaking:
            stat, sc = "◉  SPEAKING  ◉", C_GOLD
        else:
            sym  = "◉" if self.status_blink else "◎"
            stat = f"{sym}  {self.status_text}  {sym}"
            sc   = C_PRI
        c.create_text(W // 2, sy, text=stat,
                      fill=sc, font=("Courier", 12, "bold"))

        # waveform
        wy  = sy + 26
        N   = 40
        BH  = 22
        bw  = 7
        total_w = N * bw
        wx0     = (W - total_w) // 2
        for i in range(N):
            if self.speaking:
                hb  = random.randint(3, BH)
                col = C_PRI if hb > BH * 0.55 else C_GOLD
            else:
                hb  = int(3 + 2.5 * math.sin(t * 0.07 + i * 0.52))
                col = C_DIM
            bx = wx0 + i * bw
            c.create_rectangle(bx, wy + BH - hb, bx + bw - 1, wy + BH,
                                fill=col, outline="")

    def _draw_side_panels(self, c, W, H, FCX, FCY, FW):
        """Two data panels flanking the central display."""
        panel_w = int((W - FW * 1.18) / 2) - 12
        if panel_w < 60:
            return

        py    = int(FCY - FW * 0.42)
        ph    = int(FW * 0.85)
        lx    = 14
        rx    = W - 14 - panel_w

        for side_x in (lx, rx):
            # panel border
            c.create_rectangle(side_x, py, side_x + panel_w, py + ph,
                               outline=C_DIM, fill=C_PANEL, width=1)
            # gold top accent
            c.create_rectangle(side_x, py, side_x + panel_w, py + 2,
                               fill=C_GOLD, outline="")

            # header label
            label = "DIAGNOSTICS" if side_x == lx else "SYSTEMS"
            c.create_text(side_x + panel_w // 2, py + 12,
                          text=label, fill=C_GOLD,
                          font=("Courier", 7, "bold"))

            # data rows
            rows = self._data_left if side_x == lx else self._data_right
            keys_l = ["NEURAL", "POWER", "SIGNAL", "LATENCY", "MEMORY", "SYNC", "CORE", "NET"]
            keys_r = ["VISION", "AUDIO", "MOTOR", "SENSOR", "THERMO", "VOLT", "AMP", "PROC"]
            keys   = keys_l if side_x == lx else keys_r
            for i, (k, v) in enumerate(zip(keys, rows)):
                ry = py + 26 + i * 20
                c.create_text(side_x + 6, ry, text=k,
                              fill=C_MID, font=("Courier", 7), anchor="w")
                c.create_text(side_x + panel_w - 6, ry, text=v,
                              fill=C_GREEN if self.speaking else C_DIM,
                              font=("Courier", 7), anchor="e")
                # mini bar
                bar_w = panel_w - 12
                frac  = float(v) / 999.0
                c.create_rectangle(side_x + 6, ry + 5,
                                   side_x + 6 + bar_w, ry + 7,
                                   fill=C_DIMMER, outline="")
                c.create_rectangle(side_x + 6, ry + 5,
                                   side_x + 6 + int(bar_w * frac), ry + 7,
                                   fill=(C_GOLD if frac > 0.7 else C_PRI), outline="")

    def _draw_footer(self, c, W, H):
        FH = 26
        c.create_rectangle(0, H - FH, W, H, fill="#00060e", outline="")
        c.create_line(0, H - FH, W, H - FH, fill=C_GOLD, width=1)
        c.create_text(W // 2, H - 13, fill=C_DIM, font=("Courier", 8),
                      text=f"STARK INDUSTRIES  ·  CLASSIFIED  ·  {MODEL_BADGE.upper()}  ·  AUTHORIZED PERSONNEL ONLY")

    # ── public API ────────────────────────────────────────────────────────────

    def write_log(self, text: str):
        self.typing_queue.append(text)
        tl = text.lower()
        self.status_text = ("PROCESSING" if tl.startswith("you:")
                            else "RESPONDING" if tl.startswith("ai:")
                            else self.status_text)
        if not self.is_typing:
            self._start_typing()

    def _start_typing(self):
        if not self.typing_queue:
            self.is_typing = False
            if not self.speaking:
                self.status_text = "ONLINE"
            return
        self.is_typing = True
        text = self.typing_queue.popleft()
        tl   = text.lower()
        tag  = "you" if tl.startswith("you:") else "ai" if tl.startswith("ai:") else "sys"
        self.log_text.configure(state="normal")
        self._type_char(text, 0, tag)

    def _type_char(self, text, i, tag):
        if i < len(text):
            self.log_text.insert(tk.END, text[i], tag)
            self.log_text.see(tk.END)
            self.root.after(7, self._type_char, text, i + 1, tag)
        else:
            self.log_text.insert(tk.END, "\n")
            self.log_text.configure(state="disabled")
            self.root.after(20, self._start_typing)

    def start_speaking(self):
        self.speaking    = True
        self.status_text = "SPEAKING"

    def stop_speaking(self):
        self.speaking    = False
        self.status_text = "ONLINE"

    def _api_keys_exist(self):
        key = os.getenv("GEMINI_API_KEY", "")
        # Real keys are long and don't contain placeholders like [ or ]
        if len(key) < 20 or "[" in key or "]" in key or "YOUR_" in key.upper():
            return False
        return True

    def wait_for_api_key(self):
        while not self._api_key_ready:
            time.sleep(0.1)

    def _show_setup_ui(self):
        self.setup_frame = tk.Frame(
            self.root, bg="#00060e",
            highlightbackground=C_GOLD, highlightthickness=2
        )
        self.setup_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(self.setup_frame, text="◈  INITIALISATION REQUIRED",
                 fg=C_GOLD, bg="#00060e",
                 font=("Courier", 14, "bold")).pack(pady=(20, 4))
        tk.Label(self.setup_frame,
                 text="Enter your Gemini API key to bring J.A.R.V.I.S online.",
                 fg=C_MID, bg="#00060e",
                 font=("Courier", 9)).pack(pady=(0, 12))

        tk.Label(self.setup_frame, text="GEMINI API KEY",
                 fg=C_DIM, bg="#00060e",
                 font=("Courier", 9)).pack(pady=(8, 2))
        self.gemini_entry = tk.Entry(
            self.setup_frame, width=54,
            fg=C_TEXT, bg="#00090f",
            insertbackground=C_TEXT, borderwidth=0,
            font=("Courier", 10), show="*"
        )
        self.gemini_entry.pack(pady=(0, 6))

        tk.Button(
            self.setup_frame, text="▸  INITIALISE SYSTEMS",
            command=self._save_api_keys,
            bg="#00060e", fg=C_GOLD,
            activebackground="#001a2e",
            font=("Courier", 11, "bold"),
            borderwidth=0, pady=10
        ).pack(pady=16)

    def _save_api_keys(self):
        gemini = self.gemini_entry.get().strip()
        if not gemini:
            return
        # Save to .env
        set_key(str(ENV_FILE), "GEMINI_API_KEY", gemini)
        # Reload environment
        load_dotenv(str(ENV_FILE), override=True)
        self.setup_frame.destroy()
        self._api_key_ready = True
        self.status_text = "ONLINE"
        self.write_log("SYS: Systems initialised. J.A.R.V.I.S online.")