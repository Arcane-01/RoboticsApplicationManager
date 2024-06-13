import websocket
from manager.comms.consumer_message import ManagerConsumerMessage
from manager.libs.launch_world_model import ConfigurationModel


class ConnectCmd(ManagerConsumerMessage):
    id: str = '1'
    command: str = 'connect'


class LaunchWorldCmd(ManagerConsumerMessage):
    id: str = '2'
    command: str = 'launch_world'
    data: ConfigurationModel = ConfigurationModel(
        world='gazebo',
        launch_file_path='/opt/jderobot/Launchers/simple_circuit_followingcam.launch.py')


class LaunchPrepareViz(ManagerConsumerMessage):
    id: str = '3'
    command: str = 'prepare_visualization'
    data: str = 'gazebo_rae'

# Messages sent when launching FollowLine with RA 4.5.13
launch_world = {"id": "8f35a585-a920-4a79-a84d-0badb28d9ff4",
                "command": "launch_world",
                "data": {"name": "follow_line_default_ros2",
                         "launch_file_path": "/opt/jderobot/Launchers/simple_circuit.launch.py",
                         "ros_version": "ROS2",
                         "visualization": "gazebo_rae",
                         "world": "gazebo",
                         "template": "RoboticsAcademy/exercises/static/exercises/follow_line_newmanager/python_template/",
                         "exercise_id": "follow_line_newmanager"}}

prepare_viz = {"id": "bdc885d7-33b9-4b88-8c9b-72e9f544247f",
               "command": "prepare_visualization",
               "data": "gazebo_rae"}

websocket.enableTrace(True)
ws = websocket.create_connection("ws://localhost:7163")

ws.send(ConnectCmd().json())
ws.send(LaunchWorldCmd().json())
# ws.send(LaunchPrepareViz().json())


while True:
    try:
        user_input = input()  # Ctrl+D to exit
    except EOFError:
        exit()


# Open VNC: http://127.0.0.1:6080/vnc.html