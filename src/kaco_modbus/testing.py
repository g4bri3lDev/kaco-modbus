"""Synthetic register image of a blueplanet 8.6 TL3 for tests.

Layout per SunSpec: marker at 40000, Model 1 at 40002 (len 66),
Model 103 at 40070 (len 50), end marker at 40122.
Values mirror the real unit's display (3.28 kW, 8883 kWh).
"""

from __future__ import annotations

import json
from pathlib import Path


def _string_regs(text: str, length: int) -> list[int]:
    data = text.encode("ascii").ljust(length * 2, b"\x00")
    return [int.from_bytes(data[i : i + 2], "big") for i in range(0, length * 2, 2)]


def _s16(value: int) -> int:
    return value & 0xFFFF


def _build() -> dict[int, int]:
    registers: dict[int, int] = {}

    def put(address: int, values: list[int]) -> None:
        for offset, value in enumerate(values):
            registers[address + offset] = value

    # fmt: off
    put(40000, [0x5375, 0x6E53])                       # "SunS"
    put(40002, [1, 66])                                # Model 1 header
    put(40004, _string_regs("KACO new energy", 16))    # Mn
    put(40020, _string_regs("blueplanet 8.6 TL3", 16)) # Md
    put(40036, _string_regs("", 8))                    # Opt
    put(40044, _string_regs("V1.23", 8))                # Vr
    put(40052, _string_regs("8.6TL01723456", 16))       # SN
    put(40068, [1, 0])                                 # DA + pad
    put(40070, [103, 50])                              # Model 103 header
    put(40072, [                                       # 50 data registers
        1250, 417, 416, 417, _s16(-2),                 # A, AphA-C, A_SF (0.01)
        4001, 4002, 4000, 2311, 2309, 2312, _s16(-1),  # PPV*, PhVph*, V_SF
        3280, 0,                                       # W, W_SF -> 3280 W
        4999, _s16(-2),                                # Hz -> 49.99
        3300, 0,                                       # VA
        120, 0,                                        # VAr
        995, _s16(-1),                                 # PF -> 99.5 %
        0x0087, 0x8B38, 0,                             # WH acc32 = 8_883_000, WH_SF
        845, _s16(-2),                                 # DCA -> 8.45 A
        6502, _s16(-1),                                # DCV -> 650.2 V
        3350, 0,                                       # DCW
        412, 534, 0x8000, 0x8000, _s16(-1),            # TmpCab/Snk, n/a, n/a, Tmp_SF
        4, 0xFFFF,                                     # St=MPPT, StVnd unimplemented
        0, 0,                                          # Evt1
        0, 0, 0, 0, 0, 0, 0, 0,                        # Evt2, EvtVnd1-4 (part)
        0, 0,                                          # EvtVnd4 tail
    ])
    put(40122, [0xFFFF, 0])                            # end of chain
    # fmt: on
    return registers


BLUEPLANET_86TL3_REGISTERS: dict[int, int] = _build()


def registers_from_dump(path: str | Path) -> dict[int, int]:
    """Load a register image captured by ``python -m kaco_modbus.dump --json``."""
    data = json.loads(Path(path).read_text())
    return {int(address): value for address, value in data["registers"].items()}
