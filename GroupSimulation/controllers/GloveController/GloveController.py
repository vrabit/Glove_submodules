# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 14:25:40 2024

@author: Doe
"""
import asyncio

async def handle_client(reader, writer):
    try:
        while True:
            data = await reader.read(1024)  # Adjust buffer size as needed
            if not data:
                break
                
            message = data.decode(encoding='utf-8')
            print(message)

            if writer:
                writer.write(data)  # Echo back to client (optional)
                await writer.drain()  # Ensure that the data is actually written to the client

        if writer:
            writer.close()

    except Exception:
        print('caught runtime')
        raise SystemExit("exit")


async def main():
    try:
        server = await asyncio.start_server(handle_client, '127.0.0.1', 8877)
        print("Server started on 127.0.0.1:8877")
        async with server:
            await server.serve_forever()

    except KeyboardInterrupt:
        print('KeyboardInterrupt - EXIT')
    except RuntimeError:
        print('Runtime Exception')
    except Exception:
        print('testing')
    finally:
        print('something happened')
    
    
asyncio.run(main())
