import tkinter
import customtkinter
import subprocess
import sys
import netifaces

server_process = None


# --- Custom Colors --- #
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# --- Functions --- #
# Update the server status
def update_status(is_running):
    if is_running:
        server_status.configure(text="Server Status: up")
        server_loopback_ip.configure(text="Loopback Address: 127.0.0.1:" + port_entry.get())
        server_local_ip.configure(text="Local Network Address: " + ip + ":" + port_entry.get())
    else:
        server_status.configure(text="Server Status: down")

# Start server in a subprocess to keep the GUI from freezing
def start_server():
    global server_process

    print(f"\n{bcolors.WARNING}Command: Boot Server{bcolors.ENDC}")
    if server_process == None:
        print("Booting Server...")
        server_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "python.server:app",
                "--host",
                "0.0.0.0",
                "--port",
                port_entry.get()
            ]
        )
        update_status(True)

# Shut down the server, but keep the GUI up
def stop_server():
    global server_process
    
    print(f"{bcolors.WARNING}Command: Hault Server{bcolors.ENDC}")
    if server_process:
        print("Stopping Server...")
        server_process.terminate()
        server_process.wait()
        server_process = None
        update_status(False)
        print(f"{bcolors.OKGREEN}Server Stopped!{bcolors.ENDC}")

# Force shutdown in the case the GUI is closed before shutting down the server
def force_shutdown():
    print(f"{bcolors.FAIL}Force Server Shutdown{bcolors.ENDC}")
    stop_server()
    app.destroy()


# --- Server Default Settings --- #
default_port = 7000
interface = netifaces.gateways()['default'][netifaces.AF_INET][1]
ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']


# --- Window Setup --- #
# System Settings
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

# App Frame
app = customtkinter.CTk()
app.title("Server Manager")
app.resizable(False, False)

# Backup shutdown when the window is closed
app.protocol("WM_DELETE_WINDOW", force_shutdown)

# --- UI Elements --- #
# Frames
server_status_frame = tkinter.Frame(app, bg="#242424")
port_frame = tkinter.Frame(app, bg="#242424")
server_toggle_frame = tkinter.Frame(app, bg="#242424")
server_toggle_frame.pack(side=tkinter.TOP)
port_frame.pack(side=tkinter.TOP)
server_toggle_frame.pack(side=tkinter.BOTTOM)

# Server Status
server_status = customtkinter.CTkLabel(app, text="Server Status: down")
server_loopback_ip = customtkinter.CTkLabel(app, text="Loopback Address: 127.0.0.1:" + str(default_port))
server_local_ip = customtkinter.CTkLabel(app, text="Local Network Address: " + ip + ":" + str(default_port))
server_local_ip.pack(in_=server_toggle_frame, side=tkinter.BOTTOM)
server_loopback_ip.pack(in_=server_toggle_frame, side=tkinter.BOTTOM)
server_status.pack(in_=server_toggle_frame, side=tkinter.BOTTOM)

# Port
port_label = customtkinter.CTkLabel(app, text="Port")
port_entry = customtkinter.CTkEntry(app, corner_radius=0)
port_label.pack(in_=port_frame, side=tkinter.LEFT, padx=5, pady=10)
port_entry.pack(in_=port_frame, side=tkinter.RIGHT, padx=5, pady=10)
port_entry.insert(0, str(default_port))

# Start / Stop
server_start_button = customtkinter.CTkButton(app, text="Start Server", command=start_server)
server_stop_button = customtkinter.CTkButton(app, text="Stop Server", command=stop_server)
server_start_button.pack(in_=server_toggle_frame, side=tkinter.LEFT, padx=10, pady=10)
server_stop_button.pack(in_=server_toggle_frame, side=tkinter.LEFT, padx=10, pady=10)


# Run
if __name__ == "__main__":
    app.mainloop()