import tkinter
import customtkinter
import subprocess
import sys

server_process = None


# --- Functions --- #
# Start server in a subprocess to keep the GUI from freezing
def start_server():
    global server_process

    print("Booting Server...")
    if server_process == None:
        server_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "server:app",
                "--host",
                "0.0.0.0",
                "--port",
                port_entry.get()
            ]
        )
    server_status.configure(text="Server Status: up")

# Shut down the server, but keep the GUI up
def stop_server():
    global server_process
    
    print("Stopping Server...")
    if server_process:
        server_process.terminate()
        server_process.wait()
        server_process = None
    server_status.configure(text="Server Status: down")


# --- Server Default Settings --- #
default_port = 7000

# --- Window Setup --- #
# System Settings
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

# App Frame
app = customtkinter.CTk()
app.title("Server Manager")
app.resizable(False, False)

# --- UI Elements --- #
# Frames
title_frame = tkinter.Frame(app, bg="#242424")
port_frame = tkinter.Frame(app, bg="#242424")
server_toggle_frame = tkinter.Frame(app, bg="#242424")
title_frame.pack(side=tkinter.TOP)
port_frame.pack(side=tkinter.TOP)
server_toggle_frame.pack(side=tkinter.BOTTOM)

# Server Status
server_status = customtkinter.CTkLabel(app, text="Server Status: down")
server_status.pack(in_=title_frame, padx=10, pady=10)

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