import asyncio
import websockets
import json
import time
import uuid
from utils.word_generator import WordGenerator
from utils.parameters import ParameterManager

params = ParameterManager()

COUNTDOWN_START = params.get('game', 'countdown')
MATCH_TIMEOUT = params.get('game', 'timeout')
MAX_LOBBY_CAPACITY = params.get('game', 'max_lobby_capacity')

class PlayerSession:
    def __init__(self, websocket):
        self.websocket = websocket
        self.id = str(uuid.uuid4())
        self.progress = 0
        self.wpm = 0
        self.start_time = None
        self.finished = False

class Lobby:
    def __init__(self, manager):
        self.manager = manager
        self.players = {}
        self.text = WordGenerator().get_words()
        self.started = False
        self.countdown_started = False
        self.match_start_time = None

    async def add_player(self, player):
        self.players[player.id] = player
        await self.broadcast({
            'type': 'player_joined',
            'player_id': player.id,
            'players': list(self.players.keys())
        })

        if len(self.players) == 1 and not self.countdown_started:
            asyncio.create_task(self.start_countdown(id(self)))

    async def remove_player(self, player_id):
        if player_id in self.players:
            del self.players[player_id]
            await self.broadcast({
                'type': 'player_left',
                'player_id': player_id
            })

        if not self.players:
            return True
        return False

    async def start_countdown(self, lobby_id):
        self.countdown_started = True
        for i in range(COUNTDOWN_START):
            await self.broadcast({
                'type': 'countdown',
                'seconds': COUNTDOWN_START - i
            })
            await asyncio.sleep(1)

        self.started = True
        self.match_start_time = time.time()

        word_list_indexed = [{'id': i, 'word': w} for i, w in enumerate(self.text)]
        await self.broadcast({
            'type': 'start',
            'text': word_list_indexed
        })

        asyncio.create_task(self.match_timeout_timer(lobby_id))

    async def match_timeout_timer(self, lobby_id):
        await asyncio.sleep(MATCH_TIMEOUT)
        if self.started:
            print(f"[Lobby] Match timeout reached. Ending match.")
            await self.broadcast({'type': 'match_timeout'})
            self.started = False
            await self.manager.cleanup_lobby(lobby_id)

    async def broadcast(self, message):
        if not self.players:
            return
        await asyncio.gather(*[p.websocket.send(json.dumps(message)) for p in self.players.values()])

    async def word_check(self, player_id, word, word_idx):
        if player_id not in self.players:
            return

        if word_idx >= len(self.text):
            print(f"[Lobby] Invalid word_index {word_idx} from player {player_id}")
            return

        correct_word = self.text[word_idx]
        player = self.players[player_id]

        if word.strip() == correct_word:
            player.progress += 1
            elapsed = time.time() - (player.start_time or self.match_start_time)
            player.wpm = (player.progress / elapsed) * 60 if elapsed > 0 else 0

        await self.send_progress_update()
        await self.check_end_match()

    async def send_progress_update(self):
        state = {pid: {'progress': p.progress, 'wpm': round(p.wpm, 2)} for pid, p in self.players.items()}
        await self.broadcast({
            'type': 'update',
            'players': state
        })

    async def check_end_match(self):
        if all(p.progress >= len(self.text) for p in self.players.values()):
            print(f"[Lobby] All players finished. Ending match.")
            await self.broadcast({'type': 'match_end'})
            self.started = False

class LobbyManager:
    def __init__(self):
        self.lobbies = []

    def find_or_create_lobby(self):
        for lobby in self.lobbies:
            if not lobby.started and len(lobby.players) < MAX_LOBBY_CAPACITY:
                return lobby
        lobby = Lobby(self)
        self.lobbies.append(lobby)
        return lobby

    async def cleanup_lobbies(self):
        self.lobbies = [lobby for lobby in self.lobbies if lobby.players]

    async def cleanup_lobby(self, lobby_id):
        self.lobbies = [lobby for lobby in self.lobbies if id(lobby) != lobby_id]



manager = LobbyManager()

async def handle_client(websocket):
    player = PlayerSession(websocket)
    lobby = manager.find_or_create_lobby()
    await lobby.add_player(player)

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                continue

            if 'type' not in data:
                continue

            if data['type'] == 'word':
                await lobby.word_check(player.id, data.get('word', ''), data.get('word_index', -1))

            elif data['type'] == 'new-game':
                lobby = manager.find_or_create_lobby()
                await lobby.add_player(player)

            elif data['type'] == 'leave':
                should_close = await lobby.remove_player(player.id)

    except websockets.exceptions.ConnectionClosed:
        should_close = await lobby.remove_player(player.id)
        if should_close:
            await manager.cleanup_lobbies()

async def main():
    async with websockets.serve(handle_client, "0.0.0.0", 8765, ping_interval=20, ping_timeout=10):
        print("Server running on ws://0.0.0.0:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
