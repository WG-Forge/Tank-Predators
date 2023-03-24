import socket
import struct
import json

jsonDict = dict[str, any] # alias



class ServerConnection:
    serverAddress = "wgforge-srv.wargaming.net"
    serverPort = 443


    def __init__(self):
        '''
        Opens a socket to the server.
        '''
        self.__Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__Socket.connect((self.serverAddress, self.serverPort))


    def __sendRequest(self, actionCode : int, data : jsonDict = None) -> jsonDict:
        '''
        Sends a request to the server and returns the response.

        :param actionCode: The code of the action.
        :param data: The request data dictionary.

        :return: The response of the request.
        '''
        # Convert the data to a JSON string and get its length
        if data:
            dataJson = json.dumps(data)
            dataLen = len(dataJson)
        else: # No data
            dataJson = ""
            dataLen = 0

        # Construct the message
        msg = struct.pack("<II", actionCode, dataLen) + dataJson.encode("utf-8")

        # Send the message to the server
        self.__Socket.sendall(msg)

        # Receive the response from the server
        response = self.__Socket.recv(8)

        # Unpack the response
        resultCode, dataLen = struct.unpack("<II", response)

        # Receive the response dictionary (if there's one)
        if dataLen > 0:
            data = self.__Socket.recv(dataLen) # receive
            data = data.decode("utf-8") # decode
            data = json.loads(data) # turn into dictionary
        else:
            data = ""

        # Return the response as a json dictionary
        return {"resultCode": resultCode, "data": data}
    

    def login(self, data : jsonDict) -> jsonDict:
        '''
        Logs in the player to the server.

        :param data: The login request data dictionary.
        The server expects to receive the following required values:
            name - player's name.
        The following values are not required:
            password - player's password used to verify the connection. If the player tries to connect with another password, the login will be rejected. Default: "".
            game - game's name (use it to connect to an existing game). Default: null.
            num_turns - number of game turns to be played. Default: null. (If num_turns is null, the default game length will be used.)
            num_players - number of players in the game. Default: 1.
            is_observer - defines if a player joins a server just to watch. Default: false.

        :return: The response of the request.
        '''
        return self.__sendRequest(1, data)
    

    def logout(self) -> jsonDict:
        '''
        Logs out the player and removes the player's record from the server storage.

        :return: The response of the request.
        '''
        return self.__sendRequest(2)
    

    def map(self) -> jsonDict:
        '''
        Gets the map, which represents static information about the game.

        :return: The response of the request.
        '''
        return self.__sendRequest(3)
    

    def game_state(self) -> jsonDict:
        '''
        Gets the game state, which represents dynamic information about the game.

        :return: The response of the request.
        '''
        return self.__sendRequest(4)      
      

    def game_actions(self) -> jsonDict:
        '''
        Gets a list of game actions that happened in the previous turn, representing changes between turns.

        :return: The response of the request.
        '''
        return self.__sendRequest(5)
    

    def turn(self) -> jsonDict:
        '''
        Sends a TURN action, which forces the next turn of the game. This allows players to play faster and not wait for the game's time slice.   
        The game's time slice is 10 seconds for test battles and 1 second for final battles. All players and observers must send the TURN action before the next turn can happen.

        :return: The response of the request.
        '''
        return self.__sendRequest(6)
    

    def chat(self, data : jsonDict) -> jsonDict:
        '''
        Does nothing. Just for testing and fun.

        :param data: The chat request data dictionary.
        The server expects to receive the following required values:
            message - string message

        :return: The response of the request.
        '''
        return self.__sendRequest(100, data)


    def move(self, data : jsonDict) -> jsonDict:
        '''
        Changes vehicle position.

        :param data: The move request data dictionary.
        The server expects to receive the following required values:
            vehicle_id - id of vehicle.
            target - coordinates of hex.

        :return: The response of the request.
        '''
        return self.__sendRequest(101, data)


    def shoot(self, data : jsonDict) -> jsonDict:
        '''
        Shoots to target position.

        :param data: The shoot request data dictionary.
        The server expects to receive following required values:
            vehicle_id - id of vehicle.
            target - coordinates of hex.

        :return: The response of the request.
        '''
        return self.__sendRequest(102, data)               


    def close(self) -> None:
        '''
        Closes the socket to the server.
        '''
        self.__Socket.close()