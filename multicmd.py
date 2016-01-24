#!/usr/bin/env python3

from tkinter import Menu, filedialog, messagebox
import tkinter.ttk

from jsonconfig import JSONConfig
import multiprocessing
import subprocess

def parsefile(fn=None):
	with open(fn, "r", encoding="utf-8") as tf:
		for num, line in enumerate(tf):
			yield (num,) + tuple(line.rstrip().split("\t"))

def worker(idn, cmd):
	rv = subprocess.call(cmd, 
		stdin=subprocess.DEVNULL,
		stdout=subprocess.DEVNULL,
		stderr=subprocess.DEVNULL,
		shell=True
	)

	return (idn, rv)

class Settings(JSONConfig):
	def reset(self):
		self.store = {"commands": []}

class GUI(tkinter.Frame):
	def cb_success(self, result):
		self.progress.step()
		self.cmdlist.set(result[0], column="Result", value=result[1])
	
	def cb_error(self, error):
		self.progress.step()
		print(error)
	
	def start(self, event=None):
		cmdline = self.cmdline.get()
		procs = int(self.proccount.get())
		
		self.pool = multiprocessing.Pool(processes=procs)
		
		for entry in self.cmdlist.get_children():
			item = self.cmdlist.item(entry)
			
			idn = item.get("text")
			values = item.get("values")
			
			# Skip rows that have a Result
			if values[-1] != "":
				self.progress.step()
				continue
			
			# If the cmdline is bad
			try:
				cmd = cmdline.format(*values)
			except IndexError as e:
				messagebox.showerror("Bad commandline", "Bad commandline")
				break
	
			self.pool.apply_async(
				worker,
				(idn, cmd,),
				callback=self.cb_success,
				error_callback=self.cb_error
			)
		
		self.pool.close()
	
	def stop(self, event=None):
		self.pool.terminate()
		self.progress["value"] = 0
	
	def browse(self, event=None):
		fn = filedialog.askopenfilename()
		if not fn: return
		
		# Clear old items
		curitems = self.cmdlist.get_children()
		if curitems: self.cmdlist.delete(*curitems)
		
		entries = parsefile(fn)
		headers = next(entries)[1:]
		
		self.cmdlist["columns"] = headers + ("Result",)
		
		for header in headers:
			self.cmdlist.heading(header, text=header)
			self.cmdlist.column(header, stretch=False, minwidth=10, width=100)
		for entry in entries:
			# Skip the id number but add an empty Result
			cols = entry[1:] + ("",)
			self.cmdlist.insert("", "end", text=entry[0], iid=entry[0], values=cols)
		
		self.cmdlist.heading("Result", text="Result")
		self.cmdlist.column("Result", stretch=True, minwidth=10)
		
		self.progress["value"] = 0
		self.progress["maximum"] = len(self.cmdlist.get_children())
	
	def exit(self, event=None):
		self.quit()
	
	def save(self, event=None):
		cmdline = self.cmdline.get()
	
		Settings["commands"] += [cmdline]
		self.cmdline["values"] = Settings["commands"]
	
	def forget(self, event=None):
		cmdline = self.cmdline.get()
	
		if cmdline in Settings["commands"]:
			Settings["commands"].remove(cmdline)
			Settings.save()
		
		self.cmdline["values"] = Settings["commands"]
		self.cmdline.set("")
	
	def reset(self, event=None):
		for entry in self.cmdlist.get_children():
			self.cmdlist.set(entry, column="Result", value="")
	
	def prune(self, event=None):
		for entry in self.cmdlist.get_children():
			item = self.cmdlist.item(entry)
			
			if item.get("values")[-1] == 0:
				self.cmdlist.delete(entry)
			else:
				self.cmdlist.set(entry, column="Result", value="")
	
	def __init__(self, master=None):
		tkinter.ttk.Frame.__init__(self, master)
		self.master = master
		
		self.master.geometry("500x315")
		self.master.minsize(500, 315)
		self.master.title("MultiCMD")
		
		menubar = Menu(self.master)
		filemenu = Menu(menubar, tearoff=0)
		cmdmenu = Menu(menubar, tearoff=0)
		resmenu = Menu(menubar, tearoff=0)
		
		filemenu.add_command(label="Open...", accelerator="Ctrl+O", command=self.browse)
		filemenu.add_command(label="Quit", accelerator="Ctrl+Q", command=self.quit)
		
		cmdmenu.add_command(label="Save", accelerator="Ctrl+S", command=self.save)
		cmdmenu.add_command(label="Forget", accelerator="Ctrl+F", command=self.forget)
		
		resmenu.add_command(label="Reset", accelerator="Ctrl+E", command=self.reset)
		resmenu.add_command(label="Prune", accelerator="Ctrl+R", command=self.prune)
		
		menubar.add_cascade(label="File", menu=filemenu)
		menubar.add_cascade(label="Cmdline", menu=cmdmenu)
		menubar.add_cascade(label="Results", menu=resmenu)
		
		self.master.config(menu=menubar)
		
		# Top row
		topframe = tkinter.ttk.Frame(self)
		
		self.cmdline = tkinter.ttk.Combobox(topframe, values=Settings["commands"])
		self.proccount = tkinter.Spinbox(topframe, from_=1, to=100)
		
		# Mid row
		midframe = tkinter.ttk.Frame(self)
		
		self.cmdlist = tkinter.ttk.Treeview(midframe)
		self.cmdlist["columns"] = ("Result",)
		
		self.cmdlist.heading("#0", text="#")
		self.cmdlist.column("#0", stretch=False, minwidth=10, width=50)
		self.cmdlist.heading("Result", text="Result")
		self.cmdlist.column("Result", stretch=True, minwidth=10)
		
		yscroller = tkinter.ttk.Scrollbar(midframe, orient="vertical", command=self.cmdlist.yview)
		self.cmdlist.configure(yscroll=yscroller.set)
		
		self.progress = tkinter.ttk.Progressbar(self)
		
		# Bottom row
		startbutton = tkinter.ttk.Button(self, text="Start", command=self.start)
		stopbutton = tkinter.ttk.Button(self, text="Stop", command=self.stop)
		openbutton = tkinter.ttk.Button(self, text="Open...", command=self.browse)
		
		# Pack widgets
		self.pack(expand=True, fill="both")
		
		topframe.pack(expand=False, fill="x", padx=3, pady=3)
		self.cmdline.pack(expand=True, fill="x", side="left")
		self.proccount.pack(side="right")
		
		midframe.pack(expand=True, fill="both", padx=3)
		self.cmdlist.pack(expand=True, fill="both", side="left")
		yscroller.pack(fill="y", side="right")
		
		self.progress.pack(expand=False, fill="x", padx=3,pady=3)
		
		startbutton.pack(side="left", padx=3,pady=3)
		stopbutton.pack(side="left", padx=3, pady=3)
		openbutton.pack(side="right", padx=3, pady=3)
		
		# Keybindings
		self.bind_all("<Control-o>", self.browse)
		self.bind_all("<Control-q>", self.exit)
		self.bind_all("<Control-s>", self.save)
		self.bind_all("<Control-f>", self.forget)
		self.bind_all("<Control-e>", self.reset)
		self.bind_all("<Control-r>", self.prune)
		self.bind_all("<Control-Return>", self.start)
		self.bind_all("<Control-BackSpace>", self.stop)
		
		self.master.mainloop()

if __name__ == "__main__":
	multiprocessing.freeze_support()
	Settings = Settings("multicmd-settings.json")
	root = tkinter.Tk()
	app = GUI(master=root)
	
