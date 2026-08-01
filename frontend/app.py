from __future__ import annotations

import logging
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from backend.config import AppConfig
from backend.models import ConnectionState
from backend.status_service import StatusService


COLORS = {
    "background": "#101419",
    "panel": "#171d24",
    "panel_border": "#2e3945",
    "accent": "#f4a000",
    "online": "#36c275",
    "offline": "#ef5350",
    "disabled": "#768390",
    "simulated": "#3fa7d6",
    "text": "#edf2f7",
    "muted": "#99a8b7",
}


class IndustrialHMI:
    def __init__(self, config: AppConfig, status_service: StatusService) -> None:
        self.config = config
        self.status_service = status_service
        self.log = logging.getLogger(__name__)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.root = ctk.CTk()
        self.root.title("IndustrialUI | Machine HMI")
        self.root.geometry("1440x900")
        self.root.minsize(1100, 700)
        self.root.configure(fg_color=COLORS["background"])

        self.tabs = ctk.CTkTabview(self.root, fg_color=COLORS["background"], segmented_button_selected_color=COLORS["accent"], segmented_button_selected_hover_color="#cc8500")
        self.tabs.pack(fill="both", expand=True, padx=18, pady=18)
        self.dashboard = self.tabs.add("MACHINE OVERVIEW")
        self.settings_tab = self.tabs.add("CONFIGURATION")
        self._build_dashboard()
        self._build_settings()
        self._write_log("INFO", "IndustrialUI started. Monitoring services initialized.")
        self._refresh_statuses()

    def _panel(self, parent: ctk.CTkBaseClass) -> ctk.CTkFrame:
        return ctk.CTkFrame(parent, fg_color=COLORS["panel"], border_color=COLORS["panel_border"], border_width=1, corner_radius=8)

    def _build_dashboard(self) -> None:
        self.dashboard.grid_columnconfigure(0, weight=5)
        self.dashboard.grid_columnconfigure(1, weight=2)
        self.dashboard.grid_rowconfigure(0, weight=7)
        self.dashboard.grid_rowconfigure(1, weight=3)

        left = self._panel(self.dashboard)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(left, text="VISION / ROBOT REFERENCE", font=ctk.CTkFont(size=15, weight="bold"), text_color=COLORS["text"]).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 8))
        self.vision_canvas = tk.Canvas(left, bg="#0b0f13", highlightthickness=1, highlightbackground=COLORS["panel_border"])
        self.vision_canvas.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self.vision_canvas.bind("<Configure>", self._draw_vision_placeholder)

        right = self._panel(self.dashboard)
        right.grid(row=0, column=1, sticky="nsew", pady=(0, 10))
        ctk.CTkLabel(right, text="CONNECTION STATUS", font=ctk.CTkFont(size=15, weight="bold"), text_color=COLORS["text"]).pack(anchor="w", padx=18, pady=(16, 12))
        self.status_frame = ctk.CTkFrame(right, fg_color="transparent")
        self.status_frame.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self.status_labels: dict[str, ctk.CTkLabel] = {}

        bottom = self._panel(self.dashboard)
        bottom.grid(row=1, column=0, columnspan=2, sticky="nsew")
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_rowconfigure(1, weight=1)
        header = ctk.CTkFrame(bottom, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(12, 4))
        ctk.CTkLabel(header, text="SYSTEM LOG", font=ctk.CTkFont(size=15, weight="bold"), text_color=COLORS["text"]).pack(side="left")
        ctk.CTkButton(header, text="REFRESH", width=100, height=28, fg_color="#26313c", hover_color="#354555", command=self._refresh_statuses).pack(side="right")
        self.log_box = ctk.CTkTextbox(bottom, fg_color="#0b0f13", text_color="#c8d3dc", font=ctk.CTkFont(family="Consolas", size=12), corner_radius=5)
        self.log_box.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 14))
        self.log_box.configure(state="disabled")

    def _draw_vision_placeholder(self, _event: object = None) -> None:
        canvas = self.vision_canvas
        canvas.delete("all")
        width, height = canvas.winfo_width(), canvas.winfo_height()
        canvas.create_line(width * .15, height / 2, width * .85, height / 2, fill="#26313c", dash=(6, 5))
        canvas.create_line(width / 2, height * .15, width / 2, height * .85, fill="#26313c", dash=(6, 5))
        canvas.create_oval(width / 2 - 35, height / 2 - 35, width / 2 + 35, height / 2 + 35, outline=COLORS["accent"], width=2)
        canvas.create_text(width / 2, height / 2 + 70, text="Camera image / robot reference area", fill=COLORS["muted"], font=("Segoe UI", 12))
        canvas.create_text(18, 18, anchor="nw", text="NO IMAGE SOURCE", fill=COLORS["accent"], font=("Segoe UI", 10, "bold"))

    def _refresh_statuses(self) -> None:
        statuses = self.status_service.all_statuses()
        for child in self.status_frame.winfo_children():
            child.destroy()
        color_for = {ConnectionState.ONLINE: COLORS["online"], ConnectionState.OFFLINE: COLORS["offline"], ConnectionState.ERROR: COLORS["offline"], ConnectionState.DISABLED: COLORS["disabled"], ConnectionState.SIMULATED: COLORS["simulated"]}
        for status in statuses:
            row = ctk.CTkFrame(self.status_frame, fg_color="#202831", corner_radius=5)
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=status.name.upper(), font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text"]).pack(side="left", padx=12, pady=10)
            ctk.CTkLabel(row, text=status.state.value, font=ctk.CTkFont(size=11, weight="bold"), text_color=color_for[status.state]).pack(side="right", padx=12)
            self._write_log("INFO", f"{status.name}: {status.state.value} — {status.detail}")
        interval = self.config.getint("application", "poll_interval_ms", 1000)
        self.root.after(max(interval, 500), self._refresh_statuses)

    def _write_log(self, level: str, message: str) -> None:
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{stamp}] {level:<7} {message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _build_settings(self) -> None:
        self.settings_tab.grid_columnconfigure(0, weight=1)
        self.settings_tab.grid_rowconfigure(0, weight=1)
        self.auth_panel = self._panel(self.settings_tab)
        self.auth_panel.grid(row=0, column=0, sticky="nsew")
        self._show_login()

    def _show_login(self) -> None:
        for child in self.auth_panel.winfo_children(): child.destroy()
        form = ctk.CTkFrame(self.auth_panel, fg_color="transparent")
        form.place(relx=.5, rely=.5, anchor="center")
        ctk.CTkLabel(form, text="RESTRICTED CONFIGURATION", font=ctk.CTkFont(size=22, weight="bold"), text_color=COLORS["text"]).pack(pady=(0, 10))
        ctk.CTkLabel(form, text="Authorized personnel only", text_color=COLORS["muted"]).pack(pady=(0, 20))
        self.user_entry = ctk.CTkEntry(form, width=300, placeholder_text="Username")
        self.user_entry.pack(pady=6)
        self.password_entry = ctk.CTkEntry(form, width=300, placeholder_text="Password", show="•")
        self.password_entry.pack(pady=6)
        ctk.CTkButton(form, text="UNLOCK CONFIGURATION", fg_color=COLORS["accent"], hover_color="#cc8500", text_color="#15191e", command=self._authenticate).pack(fill="x", pady=(16, 0))

    def _authenticate(self) -> None:
        if self.user_entry.get() == self.config.get("security", "username") and self.password_entry.get() == self.config.get("security", "password"):
            self._show_settings_form()
            self._write_log("INFO", "Configuration access granted.")
        else:
            messagebox.showerror("Access denied", "Invalid username or password.")
            self._write_log("WARNING", "Failed configuration login attempt.")

    def _show_settings_form(self) -> None:
        for child in self.auth_panel.winfo_children(): child.destroy()
        container = ctk.CTkScrollableFrame(self.auth_panel, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=20)
        self.config_entries: dict[tuple[str, str], ctk.CTkEntry] = {}
        ctk.CTkLabel(container, text="CONNECTION CONFIGURATION", font=ctk.CTkFont(size=20, weight="bold"), text_color=COLORS["text"]).pack(anchor="w", pady=(0, 16))
        for title, section, fields in [("PLC (SLMP)", "plc", ["host", "port"]), ("CAMERAS", "cameras", ["host", "port"]), ("ROBOT", "robot", ["host", "port"]), ("MES", "mes", ["enabled", "host", "port"])]:
            card = ctk.CTkFrame(container, fg_color="#202831", corner_radius=6)
            card.pack(fill="x", pady=7)
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["accent"]).grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(12, 8))
            for row, field in enumerate(fields, 1):
                ctk.CTkLabel(card, text=field.replace("_", " ").upper(), text_color=COLORS["muted"]).grid(row=row, column=0, sticky="w", padx=14, pady=6)
                entry = ctk.CTkEntry(card, width=350)
                entry.insert(0, self.config.get(section, field))
                entry.grid(row=row, column=1, sticky="ew", padx=14, pady=6)
                self.config_entries[(section, field)] = entry
            card.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(container, text="SAVE CONFIGURATION", fg_color=COLORS["accent"], hover_color="#cc8500", text_color="#15191e", command=self._save_configuration).pack(anchor="e", pady=18)

    def _save_configuration(self) -> None:
        for (section, field), entry in self.config_entries.items():
            self.config.set(section, field, entry.get())
        self.config.save()
        self.config.load()
        self._write_log("INFO", "Configuration saved to config.ini.")
        messagebox.showinfo("Saved", "Configuration saved. New connection settings apply on the next refresh.")

    def run(self) -> None:
        self.root.mainloop()
