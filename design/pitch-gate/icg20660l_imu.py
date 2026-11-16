"""
DFRobot Fermion ICG-20660L (SEN0443) — thin I2C driver for Raspberry Pi.

Default addr 0x69 (SDO high). WHO_AM_I expect 0x91.
Wiring (I2C): 3V3, GND, SDA→SDA, SCL→SCL. Enable I2C via raspi-config.
"""

from __future__ import annotations

import struct
import time

REG_SMPLRT_DIV = 0x19
REG_GYRO_CONFIG = 0x1B
REG_ACCEL_CONFIG = 0x1C
REG_ACCEL_XOUT_H = 0x3B
REG_GYRO_XOUT_H = 0x43
REG_PWR_MGMT_1 = 0x6B
REG_WHO_AM_I = 0x75

WHO_AM_I_EXPECT = 0x91
ADDR_SDO_H = 0x69
ADDR_SDO_L = 0x68

# ±2 g, ±250 dps (config bits = 0)
ACCEL_LSB_PER_G = 16384.0
GYRO_LSB_PER_DPS = 131.0
G = 9.80665


class ICG20660L:
    def __init__(self, bus=1, addr=ADDR_SDO_H):
        import smbus2

        self._bus = smbus2.SMBus(bus)
        self.addr = addr

    def close(self):
        self._bus.close()

    def _write(self, reg: int, val: int) -> None:
        self._bus.write_byte_data(self.addr, reg, val & 0xFF)

    def _read_block(self, reg: int, n: int) -> list[int]:
        return self._bus.read_i2c_block_data(self.addr, reg, n)

    def who_am_i(self) -> int:
        return self._bus.read_byte_data(self.addr, REG_WHO_AM_I)

    def begin(self) -> None:
        wid = self.who_am_i()
        if wid != WHO_AM_I_EXPECT:
            raise RuntimeError(f"WHO_AM_I=0x{wid:02X}, expected 0x{WHO_AM_I_EXPECT:02X}")
        # reset, wake, PLL clock
        self._write(REG_PWR_MGMT_1, 0x80)
        time.sleep(0.1)
        self._write(REG_PWR_MGMT_1, 0x01)
        time.sleep(0.05)
        self._write(REG_GYRO_CONFIG, 0x00)   # ±250 dps
        self._write(REG_ACCEL_CONFIG, 0x00)  # ±2 g
        self._write(REG_SMPLRT_DIV, 0x00)    # max internal sample rate divider

    def read_raw(self) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
        a = self._read_block(REG_ACCEL_XOUT_H, 6)
        g = self._read_block(REG_GYRO_XOUT_H, 6)
        ax, ay, az = struct.unpack(">hhh", bytes(a))
        gx, gy, gz = struct.unpack(">hhh", bytes(g))
        return (ax, ay, az), (gx, gy, gz)

    def read(self) -> dict[str, float]:
        (ax, ay, az), (gx, gy, gz) = self.read_raw()
        return {
            "ax_g": ax / ACCEL_LSB_PER_G,
            "ay_g": ay / ACCEL_LSB_PER_G,
            "az_g": az / ACCEL_LSB_PER_G,
            "gx_dps": gx / GYRO_LSB_PER_DPS,
            "gy_dps": gy / GYRO_LSB_PER_DPS,
            "gz_dps": gz / GYRO_LSB_PER_DPS,
        }
