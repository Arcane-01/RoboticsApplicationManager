from manager.manager.launcher.launcher_interface import ILauncher
from manager.manager.docker_thread.docker_thread import DockerThread
from manager.manager.vnc.vnc_server import Vnc_server
import os
import stat

class LauncherRvizRos2(ILauncher):
    display: str
    internal_port: str
    external_port: str
    running = False
    threads = []

    def run(self, callback):
        DRI_PATH = self.get_dri_path()
        ACCELERATION_ENABLED = self.check_device(DRI_PATH)
        rviz_vnc = Vnc_server()

        if ACCELERATION_ENABLED:
            rviz_vnc.start_vnc_gpu(self.display, self.internal_port, self.external_port, DRI_PATH)
            rviz_cmd = f"export DISPLAY={self.display}; export VGL_DISPLAY={DRI_PATH}; vglrun rviz2"
        else:
            rviz_vnc.start_vnc(self.display, self.internal_port, self.external_port)
            rviz_cmd = f"export DISPLAY={self.display}; rviz2"

        rviz_thread = DockerThread(rviz_cmd)
        rviz_thread.start()
        self.threads.append(rviz_thread)
        self.running = True

    def is_running(self):
        return self.running

    def terminate(self):
        for thread in self.threads:
            if thread.is_alive():
                thread.terminate()
                thread.join()
            self.threads.remove(thread)
        self.running = False

    def died(self):
        pass
