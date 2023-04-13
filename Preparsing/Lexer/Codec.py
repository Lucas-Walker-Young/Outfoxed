# --------------------------------------------------------------------------------------------------
# ------------------------------- PRE-PARSING :: UTF-8 Bytes Decoder -------------------------------
# --------------------------------------------------------------------------------------------------
from _io import BufferedReader

from typing import Iterator


# --------------------------------------------------------------------------------------------------
# ---------------------------------- CLASS :: UTF-8 Bytes Decoder ----------------------------------
# --------------------------------------------------------------------------------------------------
class Codec(object):

    # ------------------------------------------------------------------------------------------
    # -------------------------------- ATTRIBUTES :: Attributes --------------------------------
    # ------------------------------------------------------------------------------------------
    buffer : BufferedReader
    offset : int

    codepoint_a : int
    codepoint_b : int

    decoder : Iterator[int]


    # ------------------------------------------------------------------------------------------
    # ------------------------------- CONSTRUCTOR :: Constructor -------------------------------
    # ------------------------------------------------------------------------------------------
    def __init__(self, source: str):

        self.buffer = open(source, mode='rb')
        self.offset = 0

        self.codepoint_a = 0
        self.codepoint_b = 0

        self.decoder = self.decode()
        self.next()
        self.next()


    # ------------------------------------------------------------------------------------------
    # ---------------------------- METHOD :: Observe the Next Byte -----------------------------
    # ------------------------------------------------------------------------------------------
    def observe(self):

        observed = int.from_bytes(self.buffer.read(1), byteorder='big')
        self.buffer.seek(self.offset)

        return observed



    # ------------------------------------------------------------------------------------------
    # ---------------------------- METHOD :: Consume the Next Byte -----------------------------
    # ------------------------------------------------------------------------------------------
    def advance(self):

        self.offset += 1
        return int.from_bytes(self.buffer.read(1), byteorder='big')


    # ------------------------------------------------------------------------------------------
    # -------------------------- UTILITY :: Decode the Next Character --------------------------
    # ------------------------------------------------------------------------------------------
    def decode(self) -> Iterator[int]:

        while start_byte := self.observe():

            if start_byte < 0b10000000:
                yield self.advance() & 0b01111111

            elif ( start_byte & 0b11100000 ) == 0b11000000:

                codepoint =  ( self.advance() & 0b00011111 ) << 6
                codepoint |= ( self.advance() & 0b00111111 ) << 0

                yield codepoint

            elif (start_byte & 0b11110000) == 0b11100000:

                codepoint  = ( self.advance() & 0b00011111 ) << 12
                codepoint |= ( self.advance() & 0b00111111 ) <<  6
                codepoint |= ( self.advance() & 0b00111111 ) <<  0

                yield codepoint

            elif (start_byte & 0b11111000) == 0b11110000:

                codepoint  = ( self.advance() & 0b00000111 ) << 18
                codepoint |= ( self.advance() & 0b00111111 ) << 12
                codepoint |= ( self.advance() & 0b00111111 ) <<  6
                codepoint |= ( self.advance() & 0b00111111 ) <<  0

                yield codepoint

        yield 0


    # ------------------------------------------------------------------------------------------
    # ------------------------- UTILITY :: Observe the Next Codepoint --------------------------
    # ------------------------------------------------------------------------------------------
    def peek(self, distance: int = 1) -> tuple[int, ...]:

        if distance == 2:
            return self.codepoint_b, self.codepoint_a

        return self.codepoint_b,


    # ------------------------------------------------------------------------------------------
    # ------------------------- UTILITY :: Consume the Next Codepoint --------------------------
    # ------------------------------------------------------------------------------------------
    def next(self) -> int:

        try:
            next_codepoint = next(self.decoder)

        except StopIteration:
            next_codepoint = 0

        returned = self.codepoint_b

        self.codepoint_b = self.codepoint_a
        self.codepoint_a = next_codepoint

        return returned
