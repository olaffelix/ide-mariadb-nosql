# Script para desarrollo: reinicia la app al detectar cambios en archivos .py
# Uso: python dev_run.py
import subprocess
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os

# Mejorar: solo reiniciar en eventos de escritura (modificación), no en lectura o apertura
class RestartOnChangeHandler(FileSystemEventHandler):
    def __init__(self, run_cmd):
        self.run_cmd = run_cmd
        self.process = None
        self.restart()

    def restart(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
        self.process = subprocess.Popen(self.run_cmd)

    def on_modified(self, event):
        # Ignorar cambios en __pycache__, archivos .pyc y el propio dev_run.py
        if (
            event.src_path.endswith('.py') and
            '__pycache__' not in event.src_path and
            not event.src_path.endswith('.pyc') and
            not event.src_path.endswith('dev_run.py')
        ):
            print(f"Archivo modificado: {event.src_path}. Reiniciando...")
            self.restart()

if __name__ == "__main__":
    run_cmd = [sys.executable, "main.py"]
    event_handler = RestartOnChangeHandler(run_cmd)
    observer = Observer()
    # Limitar a carpetas de código fuente para evitar reinicios por archivos fuera de src
    for watch_dir in ["ui", "db", "widgets"]:
        observer.schedule(event_handler, path=watch_dir, recursive=True)
    observer.start()
    print("Desarrollo: Observando cambios en archivos .py en ui/, db/ y widgets/. Presiona Ctrl+C para salir.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    observer.join()
