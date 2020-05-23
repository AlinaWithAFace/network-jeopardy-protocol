Network Jeopardy Protocol
===

Server Specification (ver. 1) 
-----

1. Game-master starts server. Wait for clients to subscribe. Client
   will establish a TCP connection, and send a `CM_SUBSCRIBE` message
   with team info. In `COLLECT_SUBSCRIPTIONS` state.

2. Once `MIN_PLAYERS` number of players have subscribed
   (i.e., `MIN_PLAYERS` players have an *active* TCP connection with the
   server), the game has started. Send `SM_NEW_GAME` to all players,
   notifying them that a new game has begun. In `GAME_IN_PROGRESS`
   state.

   NOTE: A player that has joined may leave before `MIN_PLAYERS`
   join. When you *think* you have `MIN_PLAYERS`, check to make sure
   nobody disconnected. If anyone did, then continue `accept()`ing more
   connections.

3. Game-master clicks on "Start Round." If a player is not already
   selected (i.e., first round), pick a player at random. ``Broadcast''
   an `SM_NEW_ROUND` message. This message will carry the selected
   player's name. In `ROUND_IN_PROGRESS` state.

4. If a `CM_CATEGORY` message is received, ensure that the message was
   sent by the selected player. Notify all players of choice through
   an `SM_CATEGORY` message broadcast. In `CATEGORY_SELECTED` state.

6. Game-master sends `SM_QUESTION` to players, letting all players know 
   the current question. Then Game-master stays idle, waiting for the 
   first `CM_RING` message. In `WAIT_FOR_RING` state.

7. Once the first `CM_RING` message comes, Game-master stops accepting
   any other `CM_RING` messages and sends `SM_RING_CLIENT` message to all
   players, letting they know who is picked up to answer the current
   question. Then Game-master waits for the answer. In
   `WAIT_FOR_CM_ANSWER` state.

8. If a `CM_ANSWER` message is received, ensure that the message was
   sent by the selected player and then check whether the answer is
   correct. Broadcast `SM_ANSWER` to all players, telling them the
   answer from the player and whether the answer is correct. In
   `END_OF_ROUND` state.



Client Specification (ver. 1) 
----

1. Player starts client. Send `CM_SUBSCRIBE` message to the
   server. In `JOINING_GAME` state.

2. `SM_NEW_GAME` message received from server. Update state and display
   info to player. In `GAME_IN_PROGRESS` state.

3. `SM_NEW_ROUND` message received from server which includes the
   selected player's name. In `ROUND_IN_PROGRESS` state.

   1. If selected player is this player, wait for player to choose
      category. Send `CM_CATEGORY` message to server with chosen
      category. Continue in `ROUND_IN_PROGRESS` state.

4. `SM_CATEGORY` received from server, carrying the category selected
   for this round. Display this info to the player. In
   `CATEGORY_SELECTED` state.

5. `SM_QUESTION` received from server, carry the question for this
   round. Display the question to player, start a ring-in timer and
   wait for player to ring in. In `DISPLAY_QUESTION` state.

6. Once player rings in before the ring-in timer expires and
   `SM_RING_CLIENT` message is received, sends `CM_RING` message to
   server. In `DISPLAY_QUESTION` state.
  
   1. If the ring-in timer expires, change state from `DISPLAY_QUESTION`
      to `WAIT_FOR_ANSWER`. Disable player to ring in.

7. `SM_ANSWER` message received from server, further ring-in from player
   will not be accepted. Display the answer from player and the
   correct answer. In `ANSWER_SHOWN` state.

Message Definitions and Formats (ver. 1)
-----

### Server messages:


#### s0: `SM_NEW_GAME`
Message to indicate start of a new game.  
Variable number of fields: #players, player names, #categories,  category names, #questions in each category,
points per question, default timeout (in milliseconds).
Player ids are integers starting at 1, and are assigned in the order that they are listed in this message.
No player can be assigned the id 0 (reserved use).
Category ids are integers starting at 0, and are assigned in the order that they are listed in this message.

#### s1: `SM_NEW_ROUND`
Indicates start of a new round.  
1 field: player id.
	     	   
#### s2: `SM_CATEGORY`
Message carrying selected category.  
1 field: category id.

#### s3: `SM_QUESTION`
Message carrying the question of current round.  
1 field: question.

#### s4: `SM_RING_CLIENT`
Message carrying the id of the selected player to answer the question of this round.  
1 field: player id.

#### s5: `SM_ANSWER`
Message carrying correct answer from server and the answer from player.  
2 fields: correct answer and answer from player.

### Client messages:


#### c0: `CM_SUBSCRIBE`
Subscription message with player info.  
1 field: Player name.

#### c1: `CM_CATEGORY`
Selected category announcement message.  
2 fields: category id and player id.

#### c2: `CM_RING`
Telling server a player rings in.  
1 field: player id.

#### c3: `CM_ANSWER`
Answer typed by player.  
1 field: player's answer.
