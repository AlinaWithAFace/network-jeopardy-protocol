from fysom import Fysom  # https://github.com/mriehl/fysom
import socket  # https://www.tutorialspoint.com/python/python_networking.htm


class Player:
    fsm = Fysom({'initial': 'JOINING_GAME',
                 'events': [
                     {'name': 'CM_SUBSCRIBE', 'src': 'JOINING_GAME', 'dst': 'JOINING_GAME'},
                     {'name': 'CM_CATEGORY', 'src': 'ROUND_IN_PROGRESS', 'dst': 'ROUND_IN_PROGRESS'},
                     {'name': 'CM_RING', 'src': 'DISPLAY_QUESTION', 'dst': 'DISPLAY_QUESTION'},
                     {'name': 'CM_ANSWER', 'src': 'DISPLAY_QUESTION', 'dst': 'DISPLAY_QUESTION'},

                     {'name': 'timer_expired', 'src': 'DISPLAY_QUESTION', 'dst': 'WAIT_FOR_ANSWER'},

                     {'name': 'SM_NEW_GAME', 'src': 'JOINING_GAME', 'dst': 'GAME_IN_PROGRESS'},
                     {'name': 'SM_NEW_ROUND', 'src': 'GAME_IN_PROGRESS', 'dst': 'ROUND_IN_PROGRESS'},
                     {'name': 'SM_CATEGORY', 'src': 'ROUND_IN_PROGRESS', 'dst': 'CATEGORY_SELECTED'},
                     {'name': 'SM_QUESTION', 'src': 'CATEGORY_SELECTED', 'dst': 'DISPLAY_QUESTION'},
                     {'name': 'SM_RING_CLIENT', 'src': 'DISPLAY_QUESTION', 'dst': 'DISPLAY_QUESTION'},
                     {'name': 'SM_ANSWER', 'src': 'DISPLAY_QUESTION', 'dst': 'ANSWER_SHOWN'}
                 ]})


def main():
    player = Player()

    s = socket.socket()  # Create a socket object
    host = socket.gethostname()  # Get local machine name
    port = 12345  # Reserve a port for your service.

    s.connect((host, port))

    # join the game
    message = "cm_subscribe billy"
    s.send(bytes(message, encoding='utf8'))

    bytes_to_receive = 1024

    #####

    print(s.recv(bytes_to_receive).decode(encoding='utf8'))  # SM new game
    print(s.recv(bytes_to_receive).decode(encoding='utf8'))  # SM new round

    print(s.recv(bytes_to_receive).decode(encoding='utf8'))  # SM new round
    print(s.recv(bytes_to_receive).decode(encoding='utf8'))  # SM new round

    # s.close()  # Close the socket when done


main()
