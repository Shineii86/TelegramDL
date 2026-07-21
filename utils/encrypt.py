#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
    PROJECT:  TelegramDL - Advanced Telegram Downloader Bot
    AUTHOR:   Shinei Nouzen (Shineii86)
    LICENSE:  MIT License (c) 2024-2026
    REPO:     https://github.com/Shineii86/TelegramDL
============================================================================
    DESCRIPTION:
        AES-128-GCM encryption/decryption for session strings.
        Protects user sessions stored in MongoDB.

    SECURITY:
        Uses PBKDF2 key derivation with 100k iterations
        Random 12-byte nonce per encryption
        Authenticated encryption (GCM mode)

    CONFIG:
        MASTER_KEY: Encryption key (env var)
        IV_KEY:     Salt for key derivation (env var)
============================================================================
"""

import os
import base64
import logging
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from config import MASTER_KEY, IV_KEY

logger = logging.getLogger(__name__)


def derive_key(password: str = MASTER_KEY, salt: str = IV_KEY, length: int = 16) -> bytes:
    """Derive AES key from password using PBKDF2.

    Args:
        password: Master password
        salt: Salt for key derivation
        length: Key length in bytes (16 for AES-128)

    Returns:
        bytes: Derived key
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt.encode(),
        iterations=100000,
    )
    return kdf.derive(password.encode())


def encrypt_session(session_string: str) -> str:
    """Encrypt session string using AES-128-GCM.

    Args:
        session_string: Plain text session string

    Returns:
        str: Base64-encoded encrypted data (nonce + tag + ciphertext)
    """
    key = derive_key()
    nonce = os.urandom(12)
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(session_string.encode()) + encryptor.finalize()
    tag = encryptor.tag
    return base64.b64encode(nonce + tag + ciphertext).decode()


def decrypt_session(encrypted: str) -> str:
    """Decrypt session string using AES-128-GCM.

    Args:
        encrypted: Base64-encoded encrypted data

    Returns:
        str: Decrypted session string

    Raises:
        Exception: If decryption fails (wrong key, corrupted data)
    """
    key = derive_key()
    data = base64.b64decode(encrypted.encode())
    nonce = data[:12]
    tag = data[12:28]
    ciphertext = data[28:]
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag))
    decryptor = cipher.decryptor()
    return (decryptor.update(ciphertext) + decryptor.finalize()).decode()
