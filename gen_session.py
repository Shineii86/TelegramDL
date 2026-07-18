import os
import sys

try:
    from pyrogram import Client
except ImportError:
    os.system("pip install kurigram tgcrypto -q")
    from pyrogram import Client


def generate_session():
    print("=" * 50)
    print("  TelegramDL Session String Generator")
    print("=" * 50)

    api_id = int(input("\nEnter your API ID: "))
    api_hash = input("Enter your API Hash: ")
    phone = input("Enter your phone number (with country code, e.g. +1234567890): ")

    client = Client(":memory:", api_id=api_id, api_hash=api_hash)

    client.start()

    code = client.send_code(phone)
    code_str = input(f"Enter the code sent to {phone} (format: 1 2 3 4 5): ").replace(" ", "")

    try:
        client.sign_in(phone, code.phone_code_hash, code_str)
    except Exception:
        password = input("Two-step verification enabled. Enter your password: ")
        client.check_password(password)

    session_string = client.export_session_string()

    print("\n" + "=" * 50)
    print("  Your Session String:")
    print("=" * 50)
    print(session_string)
    print("=" * 50)
    print("\nCopy this session string and set it as STRING_SESSION environment variable.")

    client.stop()


if __name__ == "__main__":
    generate_session()
