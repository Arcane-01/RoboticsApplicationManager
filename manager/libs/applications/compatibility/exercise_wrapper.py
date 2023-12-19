import json
import subprocess
import sys
import threading
import time
import rosservice
import importlib
from threading import Thread

from src.manager.libs.applications.compatibility.client import Client
from src.manager.libs.process_utils import stop_process_and_children
from src.manager.ram_logging.log_manager import LogManager
from src.manager.manager.application.robotics_python_application_interface import IRoboticsPythonApplication
from src.manager.manager.lint.linter import Lint


class CompatibilityExerciseWrapper(IRoboticsPythonApplication):
    def __init__(self, exercise_command, update_callback,  gui_server):
        super().__init__(update_callback)
        self.running = False
        self.linter = Lint()
        self.brain_ready_event = threading.Event()
        self.update_callback = update_callback
        self.pick = None
        self.gui_server = gui_server
        self.exercise_command = exercise_command
        self.exercise = None

    def save_pick(self, pick):
        self.pick = pick

    def send_pick(self, pick):
        self.gui_connection.send("#pick" + json.dumps(pick))
        print("#pick" + json.dumps(pick))

    def handle_client_gui(self, msg):
        if msg['msg'] == "#pick":
            self.pick = msg['data']
        else:
            self.gui_connection.send(msg['msg'])

    def _run_server(self, cmd):
        process = subprocess.Popen(f"{cmd}", shell=True, stdout=sys.stdout, stderr=subprocess.STDOUT,
                                   bufsize=1024, universal_newlines=True)
        return process

    def run(self, code: str, exercise_id: str):
        errors = self.linter.evaluate_code(code, exercise_id)
        if errors == "":
            f = open("/workspace/code/academy.py", "w")
            f.write(code)
            f.close()
            self.exercise = self._run_server(
                f"python3 {self.exercise_command}")

            rosservice.call_service("/gazebo/unpause_physics", [])
        else:
            raise Exception(errors)



    def stop(self):
        rosservice.call_service('/gazebo/pause_physics', [])
        rosservice.call_service("/gazebo/reset_world", [])

    def resume(self):
        rosservice.call_service("/gazebo/unpause_physics", [])

    def pause(self):
        rosservice.call_service('/gazebo/pause_physics', [])

    @property
    def is_alive(self):
        return self.running

    def terminate(self):
        if self.gui_server is not None:
            try:
                stop_process_and_children(self.gui_server)
            except Exception as error:
                LogManager.logger.error(
                    f"Error al detener el servidor de la GUI: {error}")
                
        if self.exercise is not None:
            stop_process_and_children(self.exercise)

        self.running = False
