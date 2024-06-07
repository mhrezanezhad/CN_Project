import sys
from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QFont
from time import sleep
import re
import sys
import subprocess
import json
import socket 

# regex pattern for ip addres 
regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]):(6553[0-5]|654[0-9]{2}|64[0-9]{3}|[0-5]?[0-9]{0,4})$"
def check(socket) -> bool: 
    if(re.search(regex, socket)): 
        return True
    else: 
        return False
    
def run_command(command: str ) -> str:
    result = subprocess.run(command, shell=True,
                            capture_output=True, text=True)
    return result.stdout


def register(username: str, socket: str) -> dict:
    if ' ' in username or len(username) > 30:
        return {"error":"Username len must be smaller 30  without space"}
    
    if not check(socket):
        return {"error":"Use correct format for ip and port. (127.0.0.1:65535)"}
    
    command = f'curl -X POST http://127.0.0.1:5000/register -H "Content-Type: application/json" -d \'{{"username":"{username}","socket":"{socket}"}}\''
    result = run_command(command)
    return json.loads(result) 

def peers() -> dict:
    command = f'curl -X GET http://127.0.0.1:5000/peers'
    result = run_command(command)
    result = json.loads(result)
    return result


def peerinfo(username: str) -> dict:
    command = f'curl -X POST http://127.0.0.1:5000/peerinfo -H "Content-Type: application/json" -d \'{{"username":"{username}"}}\''
    result = run_command(command)
    result = json.loads(result)
    return result


def check_connectivity(ip, port):
    try:
        socket.create_connection((ip, port), timeout=5)
        return True
    except OSError:
        return False



class MyWidget(QtWidgets.QWidget):
    def __init__(self ):
        super().__init__()
        super().setGeometry(100, 100, 400, 300)        
        self.setWindowTitle("peer")
        self.layout = QtWidgets.QFormLayout()
        
        self.register_widget = None
        self.peers_widget = None
        self.chat_widget = None
        
        
        # Add main buttons
        self.register_button = QtWidgets.QPushButton("Register new peer")
        self.register_button.clicked.connect(self.open_register_widget_func)
     
        self.peers_button = QtWidgets.QPushButton("See all peers")
        self.peers_button.clicked.connect(self.open_peers_widget_func)
     
        self.chat_button = QtWidgets.QPushButton("Chat with peer")
        self.chat_button.clicked.connect(self.open_chat_widget_func)
     
        self.exit_button = QtWidgets.QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)


        self.layout.addWidget(self.register_button)
        self.layout.addWidget(self.peers_button)
        self.layout.addWidget(self.chat_button)
        self.layout.addWidget(self.exit_button)

        
        self.setLayout(self.layout)

    @QtCore.Slot()
    def peer_info_func(self):
        self.peers_button.hide()
        self.register_button.hide()
        self.peer_info_button.hide()
        self.back_button.show()

    @QtCore.Slot()
    def open_peers_widget_func(self):
        self.peers_widget = PeersWidget(self)
        self.peers_widget.setGeometry(self.geometry())
        self.peers_widget.show()
        self.hide()        


    @QtCore.Slot()
    def open_chat_widget_func(self):
        if self.chat_widget:
            self.chat_widget.show()
            self.hide()
        else:
            self.chat_widget = ChatWidget(self)
            self.chat_widget.setGeometry(self.geometry())
            self.chat_widget.show()
            self.hide()       
            
    @QtCore.Slot()
    def open_register_widget_func(self):
        if self.register_widget:
            self.register_widget.show()
            self.hide()
        else:
            self.register_widget = RegisterWidget(self)
            self.register_widget.setGeometry(self.geometry())
            self.register_widget.show()
            self.hide()

class RegisterWidget(QtWidgets.QWidget):
    def __init__(self ,old_widget):
        super().__init__()
        self.old = old_widget
        self.setWindowTitle("registering")
        self.layout = QtWidgets.QFormLayout()
       
        # Add label to show output of command 
        self.label = QtWidgets.QLabel("HIDE",self)
        self.label.setFont(QFont("Arial", 25))
        self.label.hide()
                
        # username input feild 
        self.username_text = QtWidgets.QLineEdit()
        self.username_text.setText("Enter username: ali")

        # socket input feild 
        self.socket_text = QtWidgets.QLineEdit()
        self.socket_text.setText("Enter socket: 127.0.0.1:12345")
    
        # register button 
        self.register_button = QtWidgets.QPushButton("Register")
        self.register_button.clicked.connect(self.register_func)
     
        # go menu button
        self.back_button = QtWidgets.QPushButton("Back Menu")
        self.back_button.clicked.connect(self.back_func)

        self.exit_button = QtWidgets.QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)

        # add the buttons and feilds
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.username_text)
        self.layout.addWidget(self.socket_text)
        self.layout.addWidget(self.register_button)
        self.layout.addWidget(self.back_button)
        self.layout.addWidget(self.exit_button)
        
        self.setLayout(self.layout)

    @QtCore.Slot()
    def register_func(self):
        answer = register(self.username_text.text(), self.socket_text.text())
        if answer.get("error"):
            self.label.setStyleSheet("color: red;")
            self.label.setText(answer.get("error"))
        elif answer.get("message"):
            self.label.setStyleSheet("color: green;")
            self.label.setText(answer.get("message"))
        else:
            raise Exception("UNKOWN State")
            
        self.label.show()
        
    @QtCore.Slot()
    def back_func(self):
        self.old.show()
        self.hide()

class PeersWidget(QtWidgets.QWidget):
    def __init__(self ,old_widget):
        super().__init__()
        self.old = old_widget
        self.setWindowTitle("see all peers")
        self.layout = QtWidgets.QFormLayout()

        # Add label to show output of command 
        self.label = QtWidgets.QLabel("HIDE",self)
        self.label.setFont(QFont("Arial", 25))
        self.label.hide()
     
        # go menu button
        self.back_button = QtWidgets.QPushButton("Back Menu")
        self.back_button.clicked.connect(self.back_func)

        
        all_peers = peers()
        self.peers_buttons = []
        for peer in all_peers.items():
            button = QtWidgets.QPushButton(f"{peer[0]}\n{peer[1]}")
            button.clicked.connect(self.back_func) # TODO should change to open currnet peer 
            self.peers_buttons.append(button)
            self.layout.addWidget(button)

        # exit button 
        self.exit_button = QtWidgets.QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)

        # add the buttons and feilds
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.back_button)
        self.layout.addWidget(self.exit_button)
        
        
        # add scroll bar
        scroll_area = QtWidgets.QScrollArea()
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)

        self.layout.addWidget(scroll_area)
        
        self.setLayout(self.layout)

        
    @QtCore.Slot()
    def back_func(self):
        self.old.show()
        self.deleteLater()

class ChatWidget(QtWidgets.QWidget):
    def __init__(self ,old_widget):
        super().__init__()
        self.old = old_widget
        self.setWindowTitle("see all peers")
        self.layout = QtWidgets.QFormLayout()
        
        # Add label to show output of command 
        self.label = QtWidgets.QLabel("HIDE",self)
        self.label.setFont(QFont("Arial", 25))
        self.label.hide()
        
        # username input feild 
        self.username_text = QtWidgets.QLineEdit()
        self.username_text.setText("Enter username: ali")

        # find the peer is correct open chat 
        self.open_chat_button = QtWidgets.QPushButton("Start Chat")
        self.open_chat_button.clicked.connect(self.back_func) # TODO should change to open currnet 
        self.open_chat_button.hide() 
        
        # go menu button
        self.back_button = QtWidgets.QPushButton("Back Menu")
        self.back_button.clicked.connect(self.back_func)

        # find the peer is correct open chat 
        self.peer_find_button = QtWidgets.QPushButton("Find the Peer")
        self.peer_find_button.clicked.connect(lambda:  self.find_the_peer_func(self.username_text.text()))

        # exit button 
        self.exit_button = QtWidgets.QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)

        # add the buttons and feilds
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.username_text)
        self.layout.addWidget(self.open_chat_button)
        self.layout.addWidget(self.peer_find_button)
        self.layout.addWidget(self.back_button)
        self.layout.addWidget(self.exit_button)
        
        self.setLayout(self.layout)
    
    @QtCore.Slot()
    def open_chat_func(self):
        self.old.show()
        self.hide()

    @QtCore.Slot()
    def find_the_peer_func(self , username):
        self.label.hide()
        peer = peerinfo(username)
        if  peer.get("error"):
            self.label.setStyleSheet("color: red;")
            self.label.setText(peer.get("error"))
            self.label.show()
        elif peer.get("socket"):
            socket = peer.get("socket")
            self.open_chat_button.setText(f"{username}\n{socket}")
            self.open_chat_button.show()
            self.peer_find_button.hide()
        else:
            raise Exception("UNKOWN error")
        
        
    @QtCore.Slot()
    def back_func(self):
        self.open_chat_button.hide()
        self.peer_find_button.show()
        self.old.show()
        self.hide()
        



if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setFont(QFont("Arial",20))
    widget = MyWidget()
    widget.setFixedSize(800, 400)
    widget.show()

    sys.exit(app.exec())


