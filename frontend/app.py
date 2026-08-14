from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tkinter import messagebox
import customtkinter as ctk

from backend.config import AppConfig
from backend.models import ConnectionState
from backend.status_service import StatusService
from backend.unit_logs import UnitCsvLogger

C = {"bg":"#0c1117", "panel":"#151d26", "line":"#2c3946", "accent":"#f5a000", "text":"#edf3f7", "muted":"#94a3b2", "green":"#37c477", "red":"#ef5350", "blue":"#45a7d7", "gray":"#718090"}


class IndustrialHMI:
    def __init__(self, config: AppConfig, status_service: StatusService, hmi_service: object | None = None) -> None:
        self.config, self.status_service, self.hmi_service = config, status_service, hmi_service
        self.csv_logger = UnitCsvLogger(config, Path(__file__).resolve().parent.parent)
        self.root = ctk.CTk(); self.root.title("IndustrialUI | Machine HMI"); self.root.geometry("1440x900"); self.root.minsize(1120, 720); self.root.configure(fg_color=C["bg"])
        ctk.set_appearance_mode("dark")
        self.tabs = ctk.CTkTabview(self.root, fg_color=C["bg"], segmented_button_selected_color=C["accent"], segmented_button_selected_hover_color="#cf8500")
        self.tabs.pack(fill="both", expand=True, padx=18, pady=18)
        self.overview = self.tabs.add("OVERVIEW"); self.settings = self.tabs.add("CONFIGURATION"); self.sensors = self.tabs.add("SENSOR STATES"); self.statistics = self.tabs.add("PRODUCTION STATISTICS"); self.alarms = self.tabs.add("ALARM MANAGEMENT"); self.logs = self.tabs.add("DATA STORAGE")
        self._build_overview(); self._build_settings(); self._build_sensors(); self._build_statistics(); self._build_alarms(); self._build_logs(); self._refresh()

    def panel(self, parent): return ctk.CTkFrame(parent, fg_color=C["panel"], border_color=C["line"], border_width=1, corner_radius=8)
    def title(self, parent, text): return ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=14, weight="bold"), text_color=C["text"])

    def _build_overview(self):
        self.overview.grid_columnconfigure(0, weight=5); self.overview.grid_columnconfigure(1, weight=3); self.overview.grid_rowconfigure(0, weight=7); self.overview.grid_rowconfigure(1, weight=3)
        state = self.panel(self.overview); state.grid(row=0,column=0,sticky="nsew",padx=(0,10),pady=(0,10)); state.grid_rowconfigure(1,weight=1); state.grid_columnconfigure(0,weight=1)
        self.title(state,"MACHINE STATE").grid(row=0,column=0,sticky="w",padx=18,pady=(16,8))
        self.state_label = ctk.CTkLabel(state,text="RUNNING",font=ctk.CTkFont(size=50,weight="bold"),text_color=C["green"]); self.state_label.grid(row=1,column=0)
        self.state_detail = ctk.CTkLabel(state,text="Machine is processing",font=ctk.CTkFont(size=17),text_color=C["muted"]); self.state_detail.grid(row=2,column=0,pady=(0,34))
        con = self.panel(self.overview); con.grid(row=0,column=1,sticky="nsew",pady=(0,10)); self.title(con,"CONNECTION STATUS").pack(anchor="w",padx=18,pady=(16,10)); self.connection_rows=ctk.CTkFrame(con,fg_color="transparent"); self.connection_rows.pack(fill="both",expand=True,padx=14,pady=(0,12))
        bottom = self.panel(self.overview); bottom.grid(row=1,column=0,sticky="nsew",padx=(0,10)); self.title(bottom,"REAL-TIME SYSTEM LOG").pack(anchor="w",padx=18,pady=(12,4)); self.system_log=ctk.CTkTextbox(bottom,fg_color="#090d12",text_color="#cdd7df",font=ctk.CTkFont(family="Consolas",size=12)); self.system_log.pack(fill="both",expand=True,padx=14,pady=(0,14)); self.system_log.configure(state="disabled")
        oee=self.panel(self.overview); oee.grid(row=1,column=1,sticky="nsew"); self.title(oee,"OEE & PRODUCTION").grid(row=0,column=0,columnspan=2,sticky="w",padx=18,pady=(12,8)); oee.grid_columnconfigure((0,1),weight=1)
        self.metric_labels={}
        for index,(label,value) in enumerate((("OEE","93.5%"),("TOTAL UNITS","1,248"),("TOTAL OK","1,212"),("TOTAL NG","36"),("CURRENT CT","17.8 s"),("AVERAGE CT","18.2 s"))):
            card=ctk.CTkFrame(oee,fg_color="#202a35",corner_radius=5); card.grid(row=1+index//2,column=index%2,sticky="ew",padx=7,pady=4); ctk.CTkLabel(card,text=label,font=ctk.CTkFont(size=10,weight="bold"),text_color=C["muted"]).pack(pady=(7,0)); v=ctk.CTkLabel(card,text=value,font=ctk.CTkFont(size=18,weight="bold"),text_color=C["accent"]); v.pack(pady=(0,7)); self.metric_labels[label]=v

    def _refresh(self):
        state=self.config.get("machine","status","RUNNING").upper(); color={"RUNNING":C["green"],"PAUSED":C["accent"],"ALARM":C["red"]}.get(state,C["gray"]); detail={"RUNNING":"Machine is processing","PAUSED":"Machine is paused","ALARM":"Machine alarm is active"}.get(state,"Machine state unavailable")
        self.state_label.configure(text=state,text_color=color); self.state_detail.configure(text=detail)
        for row in self.connection_rows.winfo_children(): row.destroy()
        colors={ConnectionState.ONLINE:C["green"],ConnectionState.SIMULATED:C["blue"],ConnectionState.DISABLED:C["gray"],ConnectionState.OFFLINE:C["red"],ConnectionState.ERROR:C["red"]}
        for status in self.status_service.all_statuses():
            row=ctk.CTkFrame(self.connection_rows,fg_color="#202a35",corner_radius=5); row.pack(fill="x",pady=4); ctk.CTkLabel(row,text=status.name.upper(),font=ctk.CTkFont(size=12,weight="bold"),text_color=C["text"]).pack(side="left",padx=10,pady=9); ctk.CTkLabel(row,text=status.state.value,font=ctk.CTkFont(size=11,weight="bold"),text_color=colors[status.state]).pack(side="right",padx=10)
        if self.hmi_service:
            snap = self.hmi_service.poll(); self.metric_labels["TOTAL UNITS"].configure(text=str(snap.total_output)); self.metric_labels["TOTAL OK"].configure(text=str(snap.total_ok)); self.metric_labels["TOTAL NG"].configure(text=str(snap.total_ng)); self.metric_labels["CURRENT CT"].configure(text=f"{snap.current_ct:.1f} s"); self.metric_labels["AVERAGE CT"].configure(text=f"{snap.average_ct:.1f} s"); self.metric_labels["OEE"].configure(text=(f"{(snap.availability or 0)*(snap.performance or 0)*(snap.quality or 0)*100:.1f}%" if snap.quality is not None else "N/A")); self.stats_labels["WORK ORDER"].configure(text=snap.work_order); self.stats_labels["WORK ORDER YIELD"].configure(text=f"{(snap.quality or 0)*100:.1f}%"); self._refresh_alarms()
        self._append_system_log(f"{state} | PLC monitoring status refreshed")
        self.root.after(max(1000,self.config.getint("application","poll_interval_ms",1000)),self._refresh)

    def _append_system_log(self, message):
        self.system_log.configure(state="normal"); self.system_log.insert("end",f"[{datetime.now():%H:%M:%S}] {message}\n"); self.system_log.see("end"); self.system_log.configure(state="disabled")

    def _build_settings(self):
        self.settings.grid_columnconfigure(0,weight=1); self.settings.grid_rowconfigure(0,weight=1); self.auth_panel=self.panel(self.settings); self.auth_panel.grid(sticky="nsew"); self._login()
    def _login(self):
        for child in self.auth_panel.winfo_children(): child.destroy()
        f=ctk.CTkFrame(self.auth_panel,fg_color="transparent"); f.place(relx=.5,rely=.5,anchor="center"); ctk.CTkLabel(f,text="RESTRICTED CONFIGURATION",font=ctk.CTkFont(size=22,weight="bold")).pack(pady=8); ctk.CTkLabel(f,text="Authorized personnel only",text_color=C["muted"]).pack(pady=(0,15)); self.user=ctk.CTkEntry(f,width=300,placeholder_text="Username"); self.user.pack(pady=5); self.password=ctk.CTkEntry(f,width=300,placeholder_text="Password",show="*"); self.password.pack(pady=5); ctk.CTkButton(f,text="UNLOCK CONFIGURATION",fg_color=C["accent"],text_color="#101419",command=self._authenticate).pack(fill="x",pady=15)
    def _authenticate(self):
        if self.user.get()==self.config.get("security","username") and self.password.get()==self.config.get("security","password"): self._settings_form()
        else: messagebox.showerror("Access denied","Invalid username or password.")
    def _settings_form(self):
        for child in self.auth_panel.winfo_children(): child.destroy()
        f=ctk.CTkScrollableFrame(self.auth_panel,fg_color="transparent"); f.pack(fill="both",expand=True,padx=22,pady=18); self.entries={}; self.title(f,"CONNECTION CONFIGURATION").pack(anchor="w",pady=(0,12))
        for title,section,fields in [("PLC (SLMP)","plc",["host","port"]),("CAMERAS","cameras",["host","port"]),("ROBOT","robot",["host","port"]),("PROCESS PARAMETERS","process_parameters",["pressure_lower","pressure_upper","holding_time_seconds","run_speed","inspection_lower","inspection_upper"]),("MES","mes",["enabled","host","port"]),("UNIT LOGS","unit_logs",["directory","file_name"])]:
            card=ctk.CTkFrame(f,fg_color="#202a35"); card.pack(fill="x",pady=6); ctk.CTkLabel(card,text=title,font=ctk.CTkFont(size=13,weight="bold"),text_color=C["accent"]).grid(row=0,column=0,columnspan=2,sticky="w",padx=12,pady=8); card.grid_columnconfigure(1,weight=1)
            for i,field in enumerate(fields,1):
                ctk.CTkLabel(card,text=field.replace("_"," ").upper(),text_color=C["muted"]).grid(row=i,column=0,sticky="w",padx=12,pady=5); e=ctk.CTkEntry(card); e.insert(0,self.config.get(section,field)); e.grid(row=i,column=1,sticky="ew",padx=12,pady=5); self.entries[(section,field)]=e
        ctk.CTkButton(f,text="SAVE CONFIGURATION",fg_color=C["accent"],text_color="#101419",command=self._save).pack(anchor="e",pady=14)
    def _save(self):
        for (section,field),entry in self.entries.items(): self.config.set(section,field,entry.get())
        self.config.save(); messagebox.showinfo("Saved","Configuration saved to config.ini.")

    def _build_sensors(self):
        self.sensors.grid_columnconfigure((0,1,2),weight=1); names=[s.strip() for s in self.config.get("sensors","names").split(",")]
        self.title(self.sensors,"SENSOR STATE MONITOR (OPTIONAL)").grid(row=0,column=0,columnspan=3,sticky="w",padx=8,pady=12)
        for i,name in enumerate(names):
            card=self.panel(self.sensors); card.grid(row=1+i//3,column=i%3,sticky="ew",padx=8,pady=8); ctk.CTkLabel(card,text=name.upper(),font=ctk.CTkFont(size=13,weight="bold")).pack(pady=(16,5)); active=i not in (2,5); ctk.CTkLabel(card,text="SENSING" if active else "NOT ACTIVE",text_color=C["green"] if active else C["red"],font=ctk.CTkFont(size=20,weight="bold")).pack(pady=(0,16))

    def _build_statistics(self):
        self.statistics.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.title(self.statistics, "PRODUCTION STATISTICS").grid(row=0, column=0, columnspan=4, sticky="w", padx=8, pady=12)
        self.stats_labels = {}
        for index, (label, value) in enumerate((("HOURLY CAPACITY / UPH", "N/A"), ("DAILY CAPACITY", "N/A"), ("WEEKLY CAPACITY", "N/A"), ("MONTHLY CAPACITY", "N/A"), ("WORK ORDER", "NOT CONFIGURED"), ("WORK ORDER YIELD", "N/A"), ("WORK ORDER COST", "N/A / NOT CONFIGURED"))):
            card = self.panel(self.statistics); card.grid(row=1 + index // 4, column=index % 4, sticky="nsew", padx=8, pady=8)
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=11, weight="bold"), text_color=C["muted"]).pack(padx=14, pady=(20, 5))
            value_label = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=18, weight="bold"), text_color=C["accent"]); value_label.pack(padx=14, pady=(0, 20)); self.stats_labels[label] = value_label

    def _build_alarms(self):
        self.alarms.grid_columnconfigure(0, weight=1); self.alarms.grid_rowconfigure(1, weight=1)
        card = self.panel(self.alarms); card.grid(sticky="nsew")
        self.title(card, "ALARM MANAGEMENT / HISTORY").grid(row=0, column=0, sticky="w", padx=18, pady=14)
        controls = ctk.CTkFrame(card, fg_color="transparent"); controls.grid(row=0, column=1, padx=18, pady=10)
        ctk.CTkButton(controls, text="SIMULATE ALARM", fg_color=C["red"], command=self._simulate_alarm).pack(side="left", padx=4)
        ctk.CTkButton(controls, text="CLEAR SIM-001", fg_color="#263441", command=self._clear_alarm).pack(side="left", padx=4)
        card.grid_columnconfigure(0, weight=1); card.grid_rowconfigure(1, weight=1)
        self.alarm_box = ctk.CTkTextbox(card, fg_color="#090d12", font=ctk.CTkFont(family="Consolas", size=12)); self.alarm_box.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=18, pady=(0, 18)); self._refresh_alarms()

    def _simulate_alarm(self):
        if self.hmi_service: self.hmi_service.create_simulated_alarm(); self._refresh_alarms()
    def _clear_alarm(self):
        if self.hmi_service: self.hmi_service.clear_alarm("SIM-001", "Operator"); self._refresh_alarms()
    def _refresh_alarms(self):
        if not hasattr(self, "alarm_box"): return
        rows = self.hmi_service.alarms() if self.hmi_service else []
        self.alarm_box.delete("1.0", "end"); self.alarm_box.insert("end", "No active or historical alarms.\n" if not rows else "\n".join(" | ".join(f"{k}={v}" for k,v in row.items()) for row in rows))

    def _build_logs(self):
        self.logs.grid_columnconfigure(0,weight=1); self.logs.grid_rowconfigure(1,weight=1); card=self.panel(self.logs); card.grid(sticky="nsew"); self.title(card,"UNIT CSV LOG STORAGE").grid(row=0,column=0,sticky="w",padx=18,pady=(16,4)); self.log_path=ctk.CTkLabel(card,text=str(self.csv_logger.path),text_color=C["blue"]); self.log_path.grid(row=1,column=0,sticky="w",padx=18); ctk.CTkLabel(card,text="One row is stored for every unit: timestamp, unit ID, result, cycle time, machine state and alarm code.",text_color=C["muted"]).grid(row=2,column=0,sticky="w",padx=18,pady=(2,10)); ctk.CTkButton(card,text="REFRESH RECORDS",command=self._load_records,fg_color="#263441").grid(row=0,column=1,padx=18,pady=12); card.grid_columnconfigure(0,weight=1); self.records=ctk.CTkTextbox(card,fg_color="#090d12",font=ctk.CTkFont(family="Consolas",size=12)); self.records.grid(row=3,column=0,columnspan=2,sticky="nsew",padx=18,pady=(0,18)); card.grid_rowconfigure(3,weight=1); self._load_records()
    def _load_records(self):
        rows=self.csv_logger.recent_rows(); self.records.delete("1.0","end"); self.records.insert("end","No unit records stored yet.\n" if not rows else "\n".join(" | ".join(r) for r in rows))
    def run(self): self.root.mainloop()
