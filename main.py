import tkinter
import customtkinter
import subprocess
import sys

server_process = None

# --- Functions --- #
# Start server in a subprocess to keep the GUI from freezing
def start_server():
    global server_process

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
                "7000"
            ]
        )
    server_status.configure(text="Server Status: up")

# Shut down the server, but keep the GUI up
def stop_server():
    global server_process

    if server_process:
        server_process.terminate()
        server_process.wait()
        server_process = None
    server_status.configure(text="Server Status: down")

# --- Window Setup --- #
# System Settings
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

# App Frame
app = customtkinter.CTk()
app.geometry("960x720")
app.title("Server Manager")

# --- UI Elements --- #
# Start / Stop
server_start_button = customtkinter.CTkButton(app, text="Start Server", command=start_server)
server_stop_button = customtkinter.CTkButton(app, text="Stop Server", command=stop_server)
server_start_button.pack(padx=10, pady=10)
server_stop_button.pack(padx=10, pady=10)

# Server Status
server_status = customtkinter.CTkLabel(app, text="Server Status: down")
server_status.pack(padx=10, pady=10)


# Run
if __name__ == "__main__":
    app.mainloop()