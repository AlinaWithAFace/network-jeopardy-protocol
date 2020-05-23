import traceback
import random

from fysom import Fysom, FysomGlobal  # https://github.com/mriehl/fysom
import socket  # https://www.tutorialspoint.com/python/python_networking.htm
from threading import Thread


def on_cm_subscribe(event):
    print("on_cm_subscribe")
    game_master = event.args[0]  # type: GameMaster
    client = event.args[1]
    player_name = event.args[2]

    # print("Current players={}".format(game_master.players))
    min_players = 3
    if len(game_master.players) >= min_players:
        # print("Ready to start the game!")
        print("Starting the game!")
        game_master.accepting_connections = False
        game_master.fsm.sm_new_game(game_master)
    else:
        print("Keep waiting for players")
    return


def on_sm_new_game(event):
    print("on_new_game")
    game_master = event.args[0]  # type: GameMaster

    player_names = ""
    for player in game_master.players:
        player_names += player.name

    category_names = ""
    for category in game_master.categories:
        category_names += category

    message = ""
    message += "sm_new_game"
    message += len(game_master.players)
    message += player_names
    message += len(game_master.categories)
    message += category_names
    message += game_master.questions_per_category
    message += game_master.points_per_question
    message += game_master.default_timeout

    print("Composed message: {}".format(message))

    send_clients_message(game_master, message)
    print("State: {}".format(game_master.fsm.current))
    game_master.fsm.sm_new_round(game_master)


def on_sm_new_round(event):
    print("on_sm_new_round")
    game_master = event.args[0]  # type: GameMaster
    player_index = random.randint(0, len(game_master.players))
    print("Choosing player at {}".format(player_index))
    current_player_id = game_master.players[player_index]

    message = "{} {}".format("sm_new_round", current_player_id)
    send_clients_message(game_master, message)


class GameMaster:
    players = []
    accepting_connections = True
    listening = True
    categories = ["Colors", "Animals"]
    questions_per_category = 4
    points_per_question = 10
    default_timeout = 100
    fsm = Fysom({
        'initial': 'collect_subscriptions',
        'events':
            [
                {'name': 'sm_new_game', 'src': 'collect_subscriptions', 'dst': 'game_in_progress'},
                {'name': 'sm_new_round', 'src': 'game_in_progress', 'dst': 'round_in_progress'},
                {'name': 'sm_category', 'src': 'category_selected', 'dst': 'category_selected'},
                {'name': 'sm_question', 'src': 'category_selected', 'dst': 'wait_for_ring'},
                {'name': 'sm_ring_client', 'src': 'wait_for_cm_answer', 'dst': 'wait_for_cm_answer'},
                {'name': 'sm_answer', 'src': 'end_of_round', 'dst': 'end_of_round'},

                {'name': 'cm_subscribe', 'src': 'collect_subscriptions', 'dst': 'collect_subscriptions'},
                {'name': 'cm_category', 'src': 'round_in_progress', 'dst': 'category_selected'},
                {'name': 'cm_ring', 'src': 'wait_for_ring', 'dst': 'wait_for_cm_answer'},
                {'name': 'cm_answer', 'src': 'wait_for_cm_answer', 'dst': 'end_of_round'}
            ],
        'callbacks':
            {
                'on_cm_subscribe': on_cm_subscribe,
                'on_sm_new_game': on_sm_new_game,
                'on_sm_new_round': on_sm_new_round
            }
    })

    def __init__(self):
        super(GameMaster, self).__init__()


class Player:
    def __init__(self, client):
        self.client = client
        name = ""
        player_id = None  # type: int


def main():
    # test_server()

    #####

    game_master = GameMaster()  # Set up the game master

    s = socket.socket()  # Create a socket object
    host = socket.gethostname()  # Get local machine name
    port = 12345  # Reserve a port for your service.
    s.bind((host, port))  # Bind to the port

    s.listen(5)  # Now wait for client connection.

    #####

    while game_master.accepting_connections:
        print("listening...")
        client, addr = s.accept()  # Establish connection with client.
        print('Got connection from', addr)
        player = Player(client)

        game_master.players.append(player)
        # print(game_master.players)
        try:
            Thread(target=wait_for_client_response, args=(game_master, client)).start()
        except:
            print("Thread didn't start")
            traceback.print_exc()
    s.close()


def wait_for_client_response(game_master, client):
    is_active = True
    bytes_to_receive = 1024
    while is_active:
        message: str = client.recv(bytes_to_receive).decode(encoding='utf8')
        process_message(message, client, game_master)


def process_message(m, client, game_master):
    message = m.split(' ')
    print('Received: {}'.format(message))
    command = message[0]
    args = message[1:]
    game_master.fsm.trigger(command, game_master, client, args)
    # client.send(bytes(game_master.response, encoding='utf8'))


def send_clients_message(game_master, message):
    for player in game_master.players:
        player.client.send(bytes(message, encoding='utf8'))


def test_server():
    print("testing server")
    game_master = GameMaster()

    print("Direct callback")
    game_master.fsm.cm_subscribe(game_master)

    print("indirect callback")
    message = "cm_subscribe"
    game_master.fsm.trigger(message, game_master)

    print("finished testing")


def close_connection(c):
    message = "Thank you for connecting"
    c.send(bytes(message, encoding='utf8'))
    c.shutdown(1)
    c.close()  # Close the connection


main()
