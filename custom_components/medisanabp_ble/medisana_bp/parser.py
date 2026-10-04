from __future__ import annotations

import logging
from datetime import datetime

from bluetooth_sensor_state_data import BluetoothData
from sensor_state_data import (
    SensorDeviceClass,
    Units,
)
from sensor_state_data.enum import StrEnum

_LOGGER = logging.getLogger(__name__)


class MedisanaBPSensor(StrEnum):
    SYSTOLIC = "systolic"
    DIASTOLIC = "diastolic"
    PULSE = "pulse"
    RR = "rr"
    AFIB = "afib"
    IHB = "ihb"
    TIMESTAMP = "timestamp"


class MedisanaBPBluetoothDeviceData(BluetoothData):
    """Microlife B6 Connect BLE parser."""

    def __init__(self) -> None:
        super().__init__()
        self._has_data = False

    def _start_update(self, service_info) -> None:
        """Set basic device info from BLE advertisement."""
        self.set_device_manufacturer("Microlife")
        self.set_device_type("Blood Pressure Monitor")
        name = f"{service_info.name} ({service_info.address})"
        self.set_device_name(name)
        self.set_title(name)

    # -----------------------------
    #   MAIN NOTIFY PARSER
    # -----------------------------
    def notification_handler(self, _, data: bytearray | bytes) -> None:
        """Parse Microlife B6 Connect notify packets."""

        if not data:
            return

        # Microlife sends two formats:
        # 1) ASCII string: SSSDPPPRR000
        # 2) 10-byte history packet

        # -----------------------------
        #   ASCII FORMAT
        # -----------------------------
        if len(data) >= 12 and all(32 <= b <= 126 for b in data):
            try:
                text = data.decode().strip()
                _LOGGER.debug("Microlife ASCII packet: %s", text)

                syst = int(text[0:3])
                diast = int(text[3:6])
                pulse = int(text[6:9])
                flags = int(text[9:11])

                rr = bool(flags & 0x01)
                afib = bool(flags & 0x02)
                ihb = bool(flags & 0x04)

                self._update_measurement(
                    syst=syst,
                    diast=diast,
                    pulse=pulse,
                    rr=rr,
                    afib=afib,
                    ihb=ihb,
                    timestamp=None,
                )

                self._has_data = True
                return

            except Exception as err:
                _LOGGER.warning("Failed to parse ASCII packet: %s", err)

        # -----------------------------
        #   10-BYTE HISTORY FORMAT
        # -----------------------------
        if len(data) == 10:
            try:
                syst = data[0]
                diast = data[1]
                pulse = data[2]

                year = 2000 + data[3]
                month = data[4]
                day = data[5]
                hour = data[6]
                minute = data[7]

                flags_lo = data[8]
                flags_hi = data[9]

                rr = bool(flags_lo & 0x01)
                afib = bool(flags_lo & 0x02)
                ihb = bool(flags_lo & 0x04)

                try:
                    timestamp = datetime(year, month, day, hour, minute)
                except Exception:
                    timestamp = None

                self._update_measurement(
                    syst=syst,
                    diast=diast,
                    pulse=pulse,
                    rr=rr,
                    afib=afib,
                    ihb=ihb,
                    timestamp=timestamp,
                )

                self._has_data = True
                return

            except Exception as err:
                _LOGGER.warning("Failed to parse 10-byte packet: %s", err)

        _LOGGER.debug("Unknown Microlife packet format: %s", data.hex())

    # -----------------------------
    #   SENSOR UPDATE HELPER
    # -----------------------------
    def _update_measurement(
        self,
        syst: int,
        diast: int,
        pulse: int,
        rr: bool,
        afib: bool,
        ihb: bool,
        timestamp: datetime | None,
    ) -> None:

        self.update_sensor(
            key=str(MedisanaBPSensor.SYSTOLIC),
            native_unit_of_measurement=Units.PRESSURE_MMHG,
            native_value=syst,
            device_class=SensorDeviceClass.PRESSURE,
            name="Systolic",
        )

        self.update_sensor(
            key=str(MedisanaBPSensor.DIASTOLIC),
            native_unit_of_measurement=Units.PRESSURE_MMHG,
            native_value=diast,
            device_class=SensorDeviceClass.PRESSURE,
            name="Diastolic",
        )

        self.update_sensor(
            key=str(MedisanaBPSensor.PULSE),
            native_unit_of_measurement="bpm",
            native_value=pulse,
            name="Pulse",
        )

        self.update_sensor(
            key=str(MedisanaBPSensor.RR),
            native_unit_of_measurement=None,
            native_value=rr,
            name="Irregular Rhythm (RR)",
        )

        self.update_sensor(
            key=str(MedisanaBPSensor.AFIB),
            native_unit_of_measurement=None,
            native_value=afib,
            name="AFIB Detection",
        )

        self.update_sensor(
            key=str(MedisanaBPSensor.IHB),
            native_unit_of_measurement=None,
            native_value=ihb,
            name="Irregular Heartbeat (IHB)",
        )

        if timestamp:
            self.update_sensor(
                key=str(MedisanaBPSensor.TIMESTAMP),
                native_unit_of_measurement=None,
                native_value=timestamp,
                name="Measurement Time",
            )
