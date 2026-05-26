#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import threading
import re
import platform

IS_WINDOWS = platform.system() == "Windows"

DOTFILES_PATH = os.path.expanduser("~/dotfiles/base.yml")

# ── YAML helpers ────────────────────────────────────────────────────────────

def load_snippets():
    snippets = []
    try:
        with open(DOTFILES_PATH, "r") as f:
            content = f.read()
        blocks = re.findall(r'-\s+trigger:\s*(.+?)\n\s+replace:\s*(.+)', content)
        for trigger, replace in blocks:
            snippets.append((trigger.strip(), replace.strip()))
    except Exception as e:
        messagebox.showerror("Error", f"Could not read file:\n{e}")
    return snippets

def save_snippets(snippets):
    lines = ["matches:\n"]
    for trigger, replace in snippets:
        lines.append(f"- trigger: {trigger}\n  replace: {replace}\n")
    real_path = os.path.realpath(DOTFILES_PATH)
    with open(real_path, "w") as f:
        f.writelines(lines)

# ── Git helpers ──────────────────────────────────────────────────────────────

def show_toast(message, color="#4caf50"):
    toast = tk.Toplevel(root)
    toast.overrideredirect(True)
    toast.configure(bg="#313244")
    root.update_idletasks()
    x = root.winfo_x() + root.winfo_width() // 2 - 120
    y = root.winfo_y() + root.winfo_height() // 2 - 30
    toast.geometry(f"240x60+{x}+{y}")
    tk.Label(toast, text=message, font=("Courier New", 11, "bold"),
             bg="#313244", fg=color, pady=18).pack(expand=True)
    toast.after(1500, toast.destroy)

def git_sync(on_done, status_lbl, btn_ref):
    status_lbl.config(text="Pushing to GitHub...", fg="#f0a500")
    dotfiles = os.path.expanduser("~/dotfiles")
    if IS_WINDOWS:
        cmd = f'cd /d "{dotfiles}" && git add base.yml && git commit -m "update snippets" && git push'
        restart_cmd = "espanso restart"
    else:
        cmd = f"cd '{dotfiles}' && git add base.yml && git commit -m 'update snippets' && git push"
        restart_cmd = "sleep 1 && espanso restart"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        subprocess.Popen(restart_cmd, shell=True, start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        root.after(0, lambda: on_done(True, btn_ref, status_lbl))
    else:
        root.after(0, lambda: on_done(False, btn_ref, status_lbl))

def on_sync_done(success, btn_ref, status_lbl):
    btn_ref.config(state="normal")
    if success:
        status_lbl.config(text="✓ Synced!", fg="#4caf50")
        show_toast("✓ snippet saved!")
    else:
        status_lbl.config(text="✗ Sync failed.", fg="#f44336")
        messagebox.showerror("Git error", "Could not push to GitHub.\nCheck your connection.")

# ── Theme ────────────────────────────────────────────────────────────────────

BG       = "#1e1e2e"
BG2      = "#313244"
FG       = "#cdd6f4"
ACCENT   = "#89b4fa"
GREEN    = "#4caf50"
RED      = "#f44336"
AMBER    = "#f0a500"
FONT     = ("Courier New", 11)
FONT_B   = ("Courier New", 11, "bold")
FONT_SM  = ("Courier New", 9)
FONT_LG  = ("Courier New", 15, "bold")

# ── Root ─────────────────────────────────────────────────────────────────────

root = tk.Tk()
root.title("Espanso Manager")
root.geometry("480x480")
root.resizable(True, True)
root.configure(bg=BG)

# ── Tab bar ──────────────────────────────────────────────────────────────────

tab_bar = tk.Frame(root, bg=BG)
tab_bar.pack(fill="x", padx=0, pady=0)

content = tk.Frame(root, bg=BG)
content.pack(fill="both", expand=True)
content.rowconfigure(0, weight=1)
content.columnconfigure(0, weight=1)

frames = {}
tab_btns = {}

def show_tab(name):
    for n, f in frames.items():
        f.pack_forget()
    frames[name].pack(fill="both", expand=True, padx=24, pady=16)
    for n, b in tab_btns.items():
        b.config(bg=ACCENT if n == name else BG2, fg=BG if n == name else FG)
    if name == "manage":
        refresh_list()

for tab in ["add", "manage"]:
    frames[tab] = tk.Frame(content, bg=BG)

for label, key in [("＋ Add Snippet", "add"), ("✎ Manage Snippets", "manage")]:
    b = tk.Button(tab_bar, text=label, font=FONT_B, bg=BG2, fg=FG,
                  relief="flat", bd=0, padx=16, pady=8,
                  activebackground=ACCENT, activeforeground=BG,
                  cursor="hand2", command=lambda k=key: show_tab(k))
    b.pack(side="left")
    tab_btns[key] = b

# ══ ADD TAB ══════════════════════════════════════════════════════════════════

add_frame = frames["add"]

tk.Label(add_frame, text="ESPANSO MANAGER", font=FONT_LG, bg=BG, fg=ACCENT).pack(pady=(8, 2))
tk.Label(add_frame, text="add a snippet and push to github", font=FONT_SM, bg=BG, fg="#6c7086").pack(pady=(0, 14))

tk.Label(add_frame, text="trigger", font=FONT_B, bg=BG, fg=FG, anchor="w").pack(fill="x")
trigger_entry = tk.Entry(add_frame, font=FONT, bg=BG2, fg=FG, insertbackground=FG, relief="flat", bd=6)
trigger_entry.pack(fill="x", pady=(2, 10))

tk.Label(add_frame, text="replacement", font=FONT_B, bg=BG, fg=FG, anchor="w").pack(fill="x")
replace_text = tk.Text(add_frame, font=FONT, bg=BG2, fg=FG, insertbackground=FG, relief="flat", bd=6, height=4)
replace_text.pack(fill="x", pady=(2, 14))

add_status = tk.Label(add_frame, text="", font=FONT_SM, bg=BG, fg=GREEN)
add_status.pack()

add_btn = tk.Button(add_frame, text="ADD + SYNC →", font=FONT_B,
                    bg=ACCENT, fg=BG, relief="flat", bd=0, padx=12, pady=6,
                    activebackground="#74c7ec", activeforeground=BG, cursor="hand2")
add_btn.pack(pady=(6, 0))

def do_add():
    trigger = trigger_entry.get().strip()
    replace = replace_text.get("1.0", tk.END).strip()
    if not trigger or not replace:
        messagebox.showwarning("Missing fields", "Please fill in both fields.")
        return
    snippets = load_snippets()
    snippets.append((trigger, replace))
    save_snippets(snippets)
    add_btn.config(state="disabled", text="Syncing...")
    add_status.config(text="Pushing to GitHub...", fg=AMBER)
    threading.Thread(target=git_sync, args=(on_sync_done, add_status, add_btn), daemon=True).start()
    trigger_entry.delete(0, tk.END)
    replace_text.delete("1.0", tk.END)

add_btn.config(command=do_add)

# ══ MANAGE TAB ═══════════════════════════════════════════════════════════════

mgmt_frame = frames["manage"]

tk.Label(mgmt_frame, text="MANAGE SNIPPETS", font=FONT_LG, bg=BG, fg=ACCENT).pack(pady=(0, 6))

list_frame = tk.Frame(mgmt_frame, bg=BG)
list_frame.pack(fill="both", expand=True)

scrollbar = tk.Scrollbar(list_frame, bg=BG2, troughcolor=BG)
scrollbar.pack(side="right", fill="y")

snippet_list = tk.Listbox(list_frame, font=FONT, bg=BG2, fg=FG,
                           selectbackground=ACCENT, selectforeground=BG,
                           relief="flat", bd=0, activestyle="none",
                           yscrollcommand=scrollbar.set, height=8)
snippet_list.pack(fill="both", expand=True)
scrollbar.config(command=snippet_list.yview)

edit_frame = tk.Frame(mgmt_frame, bg=BG)
edit_frame.pack(fill="x", pady=(10, 0))

tk.Label(edit_frame, text="trigger", font=FONT_B, bg=BG, fg=FG, anchor="w").grid(row=0, column=0, sticky="w")
edit_trigger = tk.Entry(edit_frame, font=FONT, bg=BG2, fg=FG, insertbackground=FG, relief="flat", bd=4, width=18)
edit_trigger.grid(row=1, column=0, padx=(0, 10), sticky="ew")

tk.Label(edit_frame, text="replacement", font=FONT_B, bg=BG, fg=FG, anchor="w").grid(row=0, column=1, sticky="w")
edit_replace = tk.Entry(edit_frame, font=FONT, bg=BG2, fg=FG, insertbackground=FG, relief="flat", bd=4)
edit_replace.grid(row=1, column=1, sticky="ew")
edit_frame.columnconfigure(1, weight=1)

btn_row = tk.Frame(mgmt_frame, bg=BG)
btn_row.pack(fill="x", pady=(8, 0))

mgmt_status = tk.Label(mgmt_frame, text="", font=FONT_SM, bg=BG, fg=GREEN)
mgmt_status.pack()

all_snippets = []

def refresh_list():
    global all_snippets
    all_snippets = load_snippets()
    snippet_list.delete(0, tk.END)
    if not all_snippets:
        return
    max_len = max(len(t) for t, r in all_snippets)
    for t, r in all_snippets:
        snippet_list.insert(tk.END, f"  {t.ljust(max_len)}  →  {r}")
def on_select(event):
    sel = snippet_list.curselection()
    if not sel:
        return
    t, r = all_snippets[sel[0]]
    edit_trigger.delete(0, tk.END)
    edit_trigger.insert(0, t)
    edit_replace.delete(0, tk.END)
    edit_replace.insert(0, r)

snippet_list.bind("<<ListboxSelect>>", on_select)

def do_save_edit():
    sel = snippet_list.curselection()
    if not sel:
        messagebox.showwarning("No selection", "Select a snippet to edit.")
        return
    idx = sel[0]
    t = edit_trigger.get().strip()
    r = edit_replace.get().strip()
    if not t or not r:
        messagebox.showwarning("Missing fields", "Fill in both fields.")
        return
    all_snippets[idx] = (t, r)
    save_snippets(all_snippets)
    refresh_list()
    save_btn.config(state="disabled")
    threading.Thread(target=git_sync, args=(on_sync_done, mgmt_status, save_btn), daemon=True).start()

def do_delete():
    sel = snippet_list.curselection()
    if not sel:
        messagebox.showwarning("No selection", "Select a snippet to delete.")
        return
    t, _ = all_snippets[sel[0]]
    if not messagebox.askyesno("Delete?", f"Delete snippet '{t}'?"):
        return
    del all_snippets[sel[0]]
    save_snippets(all_snippets)
    refresh_list()
    edit_trigger.delete(0, tk.END)
    edit_replace.delete(0, tk.END)
    delete_btn.config(state="disabled")
    threading.Thread(target=git_sync, args=(on_sync_done, mgmt_status, delete_btn), daemon=True).start()

save_btn = tk.Button(btn_row, text="SAVE EDIT →", font=FONT_B,
                     bg=ACCENT, fg=BG, relief="flat", bd=0, padx=10, pady=5,
                     cursor="hand2", command=do_save_edit)
save_btn.pack(side="left", padx=(0, 8))

delete_btn = tk.Button(btn_row, text="DELETE ✕", font=FONT_B,
                       bg=RED, fg=FG, relief="flat", bd=0, padx=10, pady=5,
                       cursor="hand2", command=do_delete)
delete_btn.pack(side="left")

# ── Start ────────────────────────────────────────────────────────────────────

show_tab("add")
root.mainloop()
