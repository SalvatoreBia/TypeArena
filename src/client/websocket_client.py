import asyncio
import websockets
import json
import sys
import termios
import tty

CLEAR_LINE = "\r\033[K"       

class Client:
    def __init__(self, uri):
        self.uri = uri

    async def run(self):
        try:
            async with websockets.connect(self.uri) as ws:
                print("Connected to server.")
                await self.listen(ws)
        except KeyboardInterrupt:
            
            print("\nInterrupted – exiting…")

    async def listen(self, ws):
        async for message in ws:
            data = json.loads(message)

            if data.get('type') == 'countdown':
                
                sys.stdout.write(f"{CLEAR_LINE}Countdown: {data['seconds']}")
                sys.stdout.flush()

            elif data.get('type') == 'start':
                text_list = data.get('text', [])
                words = ' '.join(w['word'] for w in text_list)
                print("\nGame Started!")
                print("Text to type:", words)

                try:
                    await self.typing_test(ws, text_list)
                except KeyboardInterrupt:
                    print("\nGame interrupted – goodbye!")
                    break

    async def typing_test(self, ws, text_list):
        loop = asyncio.get_event_loop()

        
        
        def read_until_space():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)  
                chars = []
                while True:
                    ch = sys.stdin.read(1)
                    if ch == "\x03":         
                        raise KeyboardInterrupt
                    if ch in (" ", "\n", "\r"):
                        break
                    chars.append(ch)
                    
                    sys.stdout.write(ch)
                    sys.stdout.flush()
                return "".join(chars)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        for w in text_list:
            wid, expected = w['id'], w['word']

            while True:
                
                sys.stdout.write(f"{CLEAR_LINE}Type [{expected}]: ")
                sys.stdout.flush()

                try:
                    user_input = await loop.run_in_executor(None, read_until_space)
                except KeyboardInterrupt:
                    raise  

                if user_input == expected:
                    
                    await ws.send(json.dumps({
                        "type": "word",
                        "word": expected,
                        "word_index": wid
                    }))
                    
                    sys.stdout.write(f"{CLEAR_LINE}")
                    sys.stdout.flush()
                    break
                else:
                    
                    sys.stdout.write(f"{CLEAR_LINE}")
                    sys.stdout.flush()
                    

        
        sys.stdout.write(f"{CLEAR_LINE}Done!\n")
        sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(Client("ws://localhost:8765").run())