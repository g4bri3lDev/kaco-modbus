"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_1.json, json/model_103.json, json/model_120.json, json/model_121.json, json/model_122.json, json/model_123.json, json/model_126.json, json/model_129.json, json/model_130.json, json/model_132.json, json/model_135.json, json/model_136.json, json/model_160.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model import Component, repeating_group
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    acc32,
    acc64,
    bitfield16,
    bitfield32,
    enum16,
    int16,
    string,
    uint16,
    uint32,
)


class OperatingState(IntEnum):
    OFF = 1
    SLEEPING = 2
    STARTING = 3
    MPPT = 4
    THROTTLED = 5
    SHUTTING_DOWN = 6
    FAULT = 7
    STANDBY = 8


class Event1(IntFlag):
    GROUND_FAULT = 1 << 0
    DC_OVER_VOLT = 1 << 1
    AC_DISCONNECT = 1 << 2
    DC_DISCONNECT = 1 << 3
    GRID_DISCONNECT = 1 << 4
    CABINET_OPEN = 1 << 5
    MANUAL_SHUTDOWN = 1 << 6
    OVER_TEMP = 1 << 7
    OVER_FREQUENCY = 1 << 8
    UNDER_FREQUENCY = 1 << 9
    AC_OVER_VOLT = 1 << 10
    AC_UNDER_VOLT = 1 << 11
    BLOWN_STRING_FUSE = 1 << 12
    UNDER_TEMP = 1 << 13
    MEMORY_LOSS = 1 << 14
    HW_TEST_FAILURE = 1 << 15


class DERTyp(IntEnum):
    PV = 4
    PV_STOR = 82


class VArAct(IntEnum):
    SWITCH = 1
    MAINTAIN = 2


class ClcTotVA(IntEnum):
    VECTOR = 1
    ARITHMETIC = 2


class ConnPh(IntEnum):
    A = 1
    B = 2
    C = 3


class PVConn(IntFlag):
    CONNECTED = 1 << 0
    AVAILABLE = 1 << 1
    OPERATING = 1 << 2
    TEST = 1 << 3


class StorConn(IntFlag):
    CONNECTED = 1 << 0
    AVAILABLE = 1 << 1
    OPERATING = 1 << 2
    TEST = 1 << 3


class ECPConn(IntFlag):
    DISCONNECTED = 1 << 0
    CONNECTED = 1 << 1


class StSetLimMsk(IntFlag):
    WMax = 1 << 0
    VAMax = 1 << 1
    VArAval = 1 << 2
    VArMaxQ1 = 1 << 3
    VArMaxQ2 = 1 << 4
    VArMaxQ3 = 1 << 5
    VArMaxQ4 = 1 << 6
    PFMinQ1 = 1 << 7
    PFMinQ2 = 1 << 8
    PFMinQ3 = 1 << 9
    PFMinQ4 = 1 << 10


class StActCtl(IntFlag):
    FixedW = 1 << 0
    FixedVAR = 1 << 1
    FixedPF = 1 << 2
    Volt_VAr = 1 << 3
    Freq_Watt_Param = 1 << 4
    Freq_Watt_Curve = 1 << 5
    Dyn_Reactive_Current = 1 << 6
    LVRT = 1 << 7
    HVRT = 1 << 8
    Watt_PF = 1 << 9
    Volt_Watt = 1 << 10
    Scheduled = 1 << 12
    LFRT = 1 << 13
    HFRT = 1 << 14


class RtSt(IntFlag):
    LVRT_ACTIVE = 1 << 0
    HVRT_ACTIVE = 1 << 1
    LFRT_ACTIVE = 1 << 2
    HFRT_ACTIVE = 1 << 3


class Conn(IntEnum):
    DISCONNECT = 0
    CONNECT = 1


class WMaxLimEna(IntEnum):
    DISABLED = 0
    ENABLED = 1


class OutPFSetEna(IntEnum):
    DISABLED = 0
    ENABLED = 1


class VArPctMod(IntEnum):
    NONE = 0
    WMax = 1
    VArMax = 2
    VArAval = 3


class VArPctEna(IntEnum):
    DISABLED = 0
    ENABLED = 1


class DeptRef(IntEnum):
    WMax = 1
    VArMax = 2
    VArAval = 3


class ReadOnly(IntEnum):
    READWRITE = 0
    READONLY = 1


class ModEna(IntFlag):
    ENABLED = 1 << 0


class VoltWattCurveDeptRef(IntEnum):
    WMax = 1
    WAval = 2


class MpptModuleOperatingState(IntEnum):
    OFF = 1
    SLEEPING = 2
    STARTING = 3
    MPPT = 4
    THROTTLED = 5
    SHUTTING_DOWN = 6
    FAULT = 7
    STANDBY = 8
    TEST = 9
    RESERVED_10 = 10


class ModuleEvents(IntFlag):
    GROUND_FAULT = 1 << 0
    INPUT_OVER_VOLTAGE = 1 << 1
    RESERVED_2 = 1 << 2
    DC_DISCONNECT = 1 << 3
    RESERVED_4 = 1 << 4
    CABINET_OPEN = 1 << 5
    MANUAL_SHUTDOWN = 1 << 6
    OVER_TEMP = 1 << 7
    RESERVED_8 = 1 << 8
    RESERVED_9 = 1 << 9
    RESERVED_10 = 1 << 10
    RESERVED_11 = 1 << 11
    BLOWN_FUSE = 1 << 12
    UNDER_TEMP = 1 << 13
    MEMORY_LOSS = 1 << 14
    ARC_DETECTION = 1 << 15
    RESERVED_16 = 1 << 16
    RESERVED_17 = 1 << 17
    RESERVED_18 = 1 << 18
    RESERVED_19 = 1 << 19
    TEST_FAILED = 1 << 20
    INPUT_UNDER_VOLTAGE = 1 << 21
    INPUT_OVER_CURRENT = 1 << 22


class GlobalEvents(IntFlag):
    GROUND_FAULT = 1 << 0
    INPUT_OVER_VOLTAGE = 1 << 1
    RESERVED_2 = 1 << 2
    DC_DISCONNECT = 1 << 3
    RESERVED_4 = 1 << 4
    CABINET_OPEN = 1 << 5
    MANUAL_SHUTDOWN = 1 << 6
    OVER_TEMP = 1 << 7
    RESERVED_8 = 1 << 8
    RESERVED_9 = 1 << 9
    RESERVED_10 = 1 << 10
    RESERVED_11 = 1 << 11
    BLOWN_FUSE = 1 << 12
    UNDER_TEMP = 1 << 13
    MEMORY_LOSS = 1 << 14
    ARC_DETECTION = 1 << 15
    RESERVED_16 = 1 << 16
    RESERVED_17 = 1 << 17
    RESERVED_18 = 1 << 18
    RESERVED_19 = 1 << 19
    TEST_FAILED = 1 << 20
    INPUT_UNDER_VOLTAGE = 1 << 21
    INPUT_OVER_CURRENT = 1 << 22


class Common(SunSpecComponent):
    """SunSpec model 1: Common."""

    mn = string(2, 16)
    """Manufacturer. Well known value registered with SunSpec for compliance."""

    md = string(18, 16)
    """Model. Manufacturer specific value (32 chars)."""

    opt = string(34, 8)
    """Options. Manufacturer specific value (16 chars)."""

    vr = string(42, 8)
    """Version. Manufacturer specific value (16 chars)."""

    sn = string(50, 16)
    """Serial Number. Manufacturer specific value (32 chars)."""

    da = uint16(66, writable=True)
    """Device Address. Modbus device address."""


class InverterThreePhase(SunSpecComponent):
    """SunSpec model 103: Inverter (Three Phase)."""

    a = uint16(2, scale_register=6, unit='A')
    """Amps. AC Current."""

    aph_a = uint16(3, scale_register=6, unit='A')
    """Amps PhaseA. Phase A Current."""

    aph_b = uint16(4, scale_register=6, unit='A')
    """Amps PhaseB. Phase B Current."""

    aph_c = uint16(5, scale_register=6, unit='A')
    """Amps PhaseC. Phase C Current."""

    pp_vph_ab = uint16(7, scale_register=13, unit='V')
    """Phase Voltage AB."""

    pp_vph_bc = uint16(8, scale_register=13, unit='V')
    """Phase Voltage BC."""

    pp_vph_ca = uint16(9, scale_register=13, unit='V')
    """Phase Voltage CA."""

    ph_vph_a = uint16(10, scale_register=13, unit='V')
    """Phase Voltage AN."""

    ph_vph_b = uint16(11, scale_register=13, unit='V')
    """Phase Voltage BN."""

    ph_vph_c = uint16(12, scale_register=13, unit='V')
    """Phase Voltage CN."""

    w = int16(14, scale_register=15, unit='W')
    """Watts. AC Power."""

    hz = uint16(16, scale_register=17, unit='Hz')
    """Hz. Line Frequency."""

    va = int16(18, scale_register=19, unit='VA')
    """VA. AC Apparent Power."""

    v_ar = int16(20, scale_register=21, unit='var')
    """VAr. AC Reactive Power."""

    pf = int16(22, scale_register=23, unit='Pct')
    """PF. AC Power Factor."""

    wh = acc32(24, scale_register=26, unit='Wh')
    """WattHours. AC Energy."""

    dca = uint16(27, scale_register=28, unit='A')
    """DC Amps. DC Current."""

    dcv = uint16(29, scale_register=30, unit='V')
    """DC Voltage."""

    dcw = int16(31, scale_register=32, unit='W')
    """DC Watts. DC Power."""

    tmp_cab = int16(33, scale_register=37, unit='C')
    """Cabinet Temperature."""

    tmp_snk = int16(34, scale_register=37, unit='C')
    """Heat Sink Temperature."""

    tmp_trns = int16(35, scale_register=37, unit='C')
    """Transformer Temperature."""

    tmp_ot = int16(36, scale_register=37, unit='C')
    """Other Temperature."""

    st = enum16(38, OperatingState)
    """Operating State."""

    st_vnd = enum16(39)
    """Vendor Operating State. Vendor specific operating state code."""

    evt1 = bitfield32(40, Event1)
    """Event1. Event fields."""

    evt2 = bitfield32(42)
    """Event Bitfield 2. Reserved for future use."""

    evt_vnd1 = bitfield32(44)
    """Vendor Event Bitfield 1. Vendor defined events."""

    evt_vnd2 = bitfield32(46)
    """Vendor Event Bitfield 2. Vendor defined events."""

    evt_vnd3 = bitfield32(48)
    """Vendor Event Bitfield 3. Vendor defined events."""

    evt_vnd4 = bitfield32(50)
    """Vendor Event Bitfield 4. Vendor defined events."""


class Nameplate(SunSpecComponent):
    """SunSpec model 120: Nameplate."""

    der_typ = enum16(2, DERTyp)
    """DERTyp. Type of DER device. Default value is 4 to indicate PV device."""

    w_rtg = uint16(3, scale_register=4, unit='W')
    """WRtg. Continuous power output capability of the inverter."""

    va_rtg = uint16(5, scale_register=6, unit='VA')
    """VARtg. Continuous Volt-Ampere capability of the inverter."""

    v_ar_rtg_q1 = int16(7, scale_register=11, unit='var')
    """VArRtgQ1. Continuous VAR capability of the inverter in quadrant 1."""

    v_ar_rtg_q2 = int16(8, scale_register=11, unit='var')
    """VArRtgQ2. Continuous VAR capability of the inverter in quadrant 2."""

    v_ar_rtg_q3 = int16(9, scale_register=11, unit='var')
    """VArRtgQ3. Continuous VAR capability of the inverter in quadrant 3."""

    v_ar_rtg_q4 = int16(10, scale_register=11, unit='var')
    """VArRtgQ4. Continuous VAR capability of the inverter in quadrant 4."""

    a_rtg = uint16(12, scale_register=13, unit='A')
    """ARtg. Maximum RMS AC current level capability of the inverter."""

    pf_rtg_q1 = int16(14, scale_register=18, unit='cos()')
    """PFRtgQ1. Minimum power factor capability of the inverter in quadrant 1."""

    pf_rtg_q2 = int16(15, scale_register=18, unit='cos()')
    """PFRtgQ2. Minimum power factor capability of the inverter in quadrant 2."""

    pf_rtg_q3 = int16(16, scale_register=18, unit='cos()')
    """PFRtgQ3. Minimum power factor capability of the inverter in quadrant 3."""

    pf_rtg_q4 = int16(17, scale_register=18, unit='cos()')
    """PFRtgQ4. Minimum power factor capability of the inverter in quadrant 4."""

    wh_rtg = uint16(19, scale_register=20, unit='Wh')
    """WHRtg. Nominal energy rating of storage device."""

    ahr_rtg = uint16(21, scale_register=22, unit='AH')
    """AhrRtg. The usable capacity of the battery. Maximum charge minus minimum
    charge from a technology capability perspective (Amp-hour capacity rating)."""

    max_cha_rte = uint16(23, scale_register=24, unit='W')
    """MaxChaRte. Maximum rate of energy transfer into the storage device."""

    max_dis_cha_rte = uint16(25, scale_register=26, unit='W')
    """MaxDisChaRte. Maximum rate of energy transfer out of the storage device."""


class Settings(SunSpecComponent):
    """SunSpec model 121: Basic Settings."""

    w_max = uint16(2, scale_register=22, writable=True, unit='W')
    """WMax. Setting for maximum power output. Default to WRtg."""

    v_ref = uint16(3, scale_register=23, writable=True, unit='V')
    """VRef. Voltage at the PCC."""

    v_ref_ofs = int16(4, scale_register=24, writable=True, unit='V')
    """VRefOfs. Offset from PCC to inverter."""

    v_max = uint16(5, scale_register=25, writable=True, unit='V')
    """VMax. Setpoint for maximum voltage."""

    v_min = uint16(6, scale_register=25, writable=True, unit='V')
    """VMin. Setpoint for minimum voltage."""

    va_max = uint16(7, scale_register=26, writable=True, unit='VA')
    """VAMax. Setpoint for maximum apparent power. Default to VARtg."""

    v_ar_max_q1 = int16(8, scale_register=27, writable=True, unit='var')
    """VArMaxQ1. Setting for maximum reactive power in quadrant 1. Default to
    VArRtgQ1."""

    v_ar_max_q2 = int16(9, scale_register=27, writable=True, unit='var')
    """VArMaxQ2. Setting for maximum reactive power in quadrant 2. Default to
    VArRtgQ2."""

    v_ar_max_q3 = int16(10, scale_register=27, writable=True, unit='var')
    """VArMaxQ3. Setting for maximum reactive power in quadrant 3. Default to
    VArRtgQ3."""

    v_ar_max_q4 = int16(11, scale_register=27, writable=True, unit='var')
    """VArMaxQ4. Setting for maximum reactive power in quadrant 4. Default to
    VArRtgQ4."""

    w_gra = uint16(12, scale_register=28, writable=True, unit='% WMax/sec')
    """WGra. Default ramp rate of change of active power due to command or internal
    action."""

    pf_min_q1 = int16(13, scale_register=29, writable=True, unit='cos()')
    """PFMinQ1. Setpoint for minimum power factor value in quadrant 1. Default to
    PFRtgQ1."""

    pf_min_q2 = int16(14, scale_register=29, writable=True, unit='cos()')
    """PFMinQ2. Setpoint for minimum power factor value in quadrant 2. Default to
    PFRtgQ2."""

    pf_min_q3 = int16(15, scale_register=29, writable=True, unit='cos()')
    """PFMinQ3. Setpoint for minimum power factor value in quadrant 3. Default to
    PFRtgQ3."""

    pf_min_q4 = int16(16, scale_register=29, writable=True, unit='cos()')
    """PFMinQ4. Setpoint for minimum power factor value in quadrant 4. Default to
    PFRtgQ4."""

    v_ar_act = enum16(17, VArAct, writable=True)
    """VArAct. VAR action on change between charging and discharging: 1=switch
    2=maintain VAR characterization."""

    clc_tot_va = enum16(18, ClcTotVA, writable=True)
    """ClcTotVA. Calculation method for total apparent power. 1=vector 2=arithmetic."""

    max_rmp_rte = uint16(19, scale_register=30, writable=True, unit='% WGra')
    """MaxRmpRte. Setpoint for maximum ramp rate as percentage of nominal maximum
    ramp rate. This setting will limit the rate that watts delivery to the grid
    can increase or decrease in response to intermittent PV generation."""

    ecp_nom_hz = uint16(20, scale_register=31, writable=True, unit='Hz')
    """ECPNomHz. Setpoint for nominal frequency at the ECP."""

    conn_ph = enum16(21, ConnPh, writable=True)
    """ConnPh. Identity of connected phase for single phase inverters. A=1 B=2 C=3."""


class Status(SunSpecComponent):
    """SunSpec model 122: Measurements_Status."""

    pv_conn = bitfield16(2, PVConn)
    """PVConn. PV inverter present/available status."""

    stor_conn = bitfield16(3, StorConn)
    """StorConn. Storage inverter present/available status."""

    ecp_conn = bitfield16(4, ECPConn)
    """ECPConn. ECP connection status: disconnected=0 connected=1."""

    act_wh = acc64(5, unit='Wh')
    """ActWh. AC lifetime active (real) energy output."""

    act_v_ah = acc64(9, unit='VAh')
    """ActVAh. AC lifetime apparent energy output."""

    act_v_arh_q1 = acc64(13, unit='varh')
    """ActVArhQ1. AC lifetime reactive energy output in quadrant 1."""

    act_v_arh_q2 = acc64(17, unit='varh')
    """ActVArhQ2. AC lifetime reactive energy output in quadrant 2."""

    act_v_arh_q3 = acc64(21, unit='varh')
    """ActVArhQ3. AC lifetime negative energy output in quadrant 3."""

    act_v_arh_q4 = acc64(25, unit='varh')
    """ActVArhQ4. AC lifetime reactive energy output in quadrant 4."""

    v_ar_aval = int16(29, scale_register=30, unit='var')
    """VArAval. Amount of VARs available without impacting watts output."""

    w_aval = uint16(31, scale_register=32, unit='W')
    """WAval. Amount of Watts available."""

    st_set_lim_msk = bitfield32(33, StSetLimMsk)
    """StSetLimMsk. Setpoint limit(s) reached."""

    st_act_ctl = bitfield32(35, StActCtl)
    """StActCtl. Which inverter controls are currently active."""

    tm_src = string(37, 4)
    """TmSrc. Source of time synchronization."""

    tms = uint32(41, unit='Secs')
    """Tms. Seconds since 01-01-2000 00:00 UTC."""

    rt_st = bitfield16(43, RtSt)
    """RtSt. Active ride-through status."""

    ris = uint16(44, scale_register=45, unit='ohms')
    """Ris. Isolation resistance."""


class Controls(SunSpecComponent):
    """SunSpec model 123: Immediate Controls."""

    conn_win_tms = uint16(2, writable=True, unit='Secs')
    """Conn_WinTms. Time window for connect/disconnect."""

    conn_rvrt_tms = uint16(3, writable=True, unit='Secs')
    """Conn_RvrtTms. Timeout period for connect/disconnect."""

    conn = enum16(4, Conn, writable=True)
    """Conn. Connection control."""

    w_max_lim_pct = uint16(5, scale_register=23, writable=True, unit='% WMax')
    """WMaxLimPct. Set power output to specified level."""

    w_max_lim_pct_win_tms = uint16(6, writable=True, unit='Secs')
    """WMaxLimPct_WinTms. Time window for power limit change."""

    w_max_lim_pct_rvrt_tms = uint16(7, writable=True, unit='Secs')
    """WMaxLimPct_RvrtTms. Timeout period for power limit."""

    w_max_lim_pct_rmp_tms = uint16(8, writable=True, unit='Secs')
    """WMaxLimPct_RmpTms. Ramp time for moving from current setpoint to new setpoint."""

    w_max_lim_ena = enum16(9, WMaxLimEna, writable=True)
    """WMaxLim_Ena. Throttle enable/disable control."""

    out_pf_set = int16(10, scale_register=24, writable=True, unit='cos()')
    """OutPFSet. Set power factor to specific value - cosine of angle."""

    out_pf_set_win_tms = uint16(11, writable=True, unit='Secs')
    """OutPFSet_WinTms. Time window for power factor change."""

    out_pf_set_rvrt_tms = uint16(12, writable=True, unit='Secs')
    """OutPFSet_RvrtTms. Timeout period for power factor."""

    out_pf_set_rmp_tms = uint16(13, writable=True, unit='Secs')
    """OutPFSet_RmpTms. Ramp time for moving from current setpoint to new setpoint."""

    out_pf_set_ena = enum16(14, OutPFSetEna, writable=True)
    """OutPFSet_Ena. Fixed power factor enable/disable control."""

    v_ar_w_max_pct = int16(15, scale_register=25, writable=True, unit='% WMax')
    """VArWMaxPct. Reactive power in percent of WMax."""

    v_ar_max_pct = int16(16, scale_register=25, writable=True, unit='% VArMax')
    """VArMaxPct. Reactive power in percent of VArMax."""

    v_ar_aval_pct = int16(17, scale_register=25, writable=True, unit='% VArAval')
    """VArAvalPct. Reactive power in percent of VArAval."""

    v_ar_pct_win_tms = uint16(18, writable=True, unit='Secs')
    """VArPct_WinTms. Time window for VAR limit change."""

    v_ar_pct_rvrt_tms = uint16(19, writable=True, unit='Secs')
    """VArPct_RvrtTms. Timeout period for VAR limit."""

    v_ar_pct_rmp_tms = uint16(20, writable=True, unit='Secs')
    """VArPct_RmpTms. Ramp time for moving from current setpoint to new setpoint."""

    v_ar_pct_mod = enum16(21, VArPctMod, writable=True)
    """VArPct_Mod. VAR percent limit mode."""

    v_ar_pct_ena = enum16(22, VArPctEna, writable=True)
    """VArPct_Ena. Percent limit VAr enable/disable control."""


class VoltVarCurve(Component):
    """One 'curve' block of SunSpec model 126."""

    act_pt = uint16(12, writable=True)
    """ActPt. Number of active points in array."""

    dept_ref = enum16(13, DeptRef, writable=True)
    """DeptRef. Meaning of dependent variable: 1=%WMax 2=%VArMax 3=%VArAval."""

    v1 = uint16(14, scale_register=9, writable=True, unit='% VRef')
    """V1. Point 1 Volts."""

    v_ar1 = int16(15, scale_register=10, writable=True)
    """VAr1. Point 1 VARs."""

    v2 = uint16(16, scale_register=9, writable=True, unit='% VRef')
    """V2. Point 2 Volts."""

    v_ar2 = int16(17, scale_register=10, writable=True)
    """VAr2. Point 2 VARs."""

    v3 = uint16(18, scale_register=9, writable=True, unit='% VRef')
    """V3. Point 3 Volts."""

    v_ar3 = int16(19, scale_register=10, writable=True)
    """VAr3. Point 3 VARs."""

    v4 = uint16(20, scale_register=9, writable=True, unit='% VRef')
    """V4. Point 4 Volts."""

    v_ar4 = int16(21, scale_register=10, writable=True)
    """VAr4. Point 4 VARs."""

    v5 = uint16(22, scale_register=9, writable=True, unit='% VRef')
    """V5. Point 5 Volts."""

    v_ar5 = int16(23, scale_register=10, writable=True)
    """VAr5. Point 5 VARs."""

    v6 = uint16(24, scale_register=9, writable=True, unit='% VRef')
    """V6. Point 6 Volts."""

    v_ar6 = int16(25, scale_register=10, writable=True)
    """VAr6. Point 6 VARs."""

    v7 = uint16(26, scale_register=9, writable=True, unit='% VRef')
    """V7. Point 7 Volts."""

    v_ar7 = int16(27, scale_register=10, writable=True)
    """VAr7. Point 7 VARs."""

    v8 = uint16(28, scale_register=9, writable=True, unit='% VRef')
    """V8. Point 8 Volts."""

    v_ar8 = int16(29, scale_register=10, writable=True)
    """VAr8. Point 8 VARs."""

    v9 = uint16(30, scale_register=9, writable=True, unit='% VRef')
    """V9. Point 9 Volts."""

    v_ar9 = int16(31, scale_register=10, writable=True)
    """VAr9. Point 9 VARs."""

    v10 = uint16(32, scale_register=9, writable=True, unit='% VRef')
    """V10. Point 10 Volts."""

    v_ar10 = int16(33, scale_register=10, writable=True)
    """VAr10. Point 10 VARs."""

    v11 = uint16(34, scale_register=9, writable=True, unit='% VRef')
    """V11. Point 11 Volts."""

    v_ar11 = int16(35, scale_register=10, writable=True)
    """VAr11. Point 11 VARs."""

    v12 = uint16(36, scale_register=9, writable=True, unit='% VRef')
    """V12. Point 12 Volts."""

    v_ar12 = int16(37, scale_register=10, writable=True)
    """VAr12. Point 12 VARs."""

    v13 = uint16(38, scale_register=9, writable=True, unit='% VRef')
    """V13. Point 13 Volts."""

    v_ar13 = int16(39, scale_register=10, writable=True)
    """VAr13. Point 13 VARs."""

    v14 = uint16(40, scale_register=9, writable=True, unit='% VRef')
    """V14. Point 14 Volts."""

    v_ar14 = int16(41, scale_register=10, writable=True)
    """VAr14. Point 14 VARs."""

    v15 = uint16(42, scale_register=9, writable=True, unit='% VRef')
    """V15. Point 15 Volts."""

    v_ar15 = int16(43, scale_register=10, writable=True)
    """VAr15. Point 15 VARs."""

    v16 = uint16(44, scale_register=9, writable=True, unit='% VRef')
    """V16. Point 16 Volts."""

    v_ar16 = int16(45, scale_register=10, writable=True)
    """VAr16. Point 16 VARs."""

    v17 = uint16(46, scale_register=9, writable=True, unit='% VRef')
    """V17. Point 17 Volts."""

    v_ar17 = int16(47, scale_register=10, writable=True)
    """VAr17. Point 17 VARs."""

    v18 = uint16(48, scale_register=9, writable=True, unit='% VRef')
    """V18. Point 18 Volts."""

    v_ar18 = int16(49, scale_register=10, writable=True)
    """VAr18. Point 18 VARs."""

    v19 = uint16(50, scale_register=9, writable=True, unit='% VRef')
    """V19. Point 19 Volts."""

    v_ar19 = int16(51, scale_register=10, writable=True)
    """VAr19. Point 19 VARs."""

    v20 = uint16(52, scale_register=9, writable=True, unit='% VRef')
    """V20. Point 20 Volts."""

    v_ar20 = int16(53, scale_register=10, writable=True)
    """VAr20. Point 20 VARs."""

    crv_nam = string(54, 8, writable=True)
    """CrvNam. Optional description for curve. (Max 16 chars)."""

    rmp_tms = uint16(62, writable=True, unit='Secs')
    """RmpTms. The time of the PT1 in seconds (time to accomplish a change of 95%)."""

    rmp_dec_tmm = uint16(63, scale_register=11, writable=True, unit='% ref_value/min')
    """RmpDecTmm. The maximum rate at which the VAR value may be reduced in response
    to changes in the voltage value. %refVal is %WMax %VArMax or %VArAval
    depending on value of DeptRef."""

    rmp_inc_tmm = uint16(64, scale_register=11, writable=True, unit='% ref_value/min')
    """RmpIncTmm. The maximum rate at which the VAR value may be increased in
    response to changes in the voltage value. %refVal is %WMax %VArMax or %VArAval
    depending on value of DeptRef."""

    read_only = enum16(65, ReadOnly)
    """ReadOnly. Boolean flag indicates if curve is read-only or can be modified."""


class VoltVar(SunSpecComponent):
    """SunSpec model 126: Static Volt-VAR."""

    act_crv = uint16(2, writable=True)
    """ActCrv. Index of active curve. 0=no active curve."""

    mod_ena = bitfield16(3, ModEna, writable=True)
    """ModEna. Is Volt-VAR control active."""

    win_tms = uint16(4, writable=True, unit='Secs')
    """WinTms. Time window for volt-VAR change."""

    rvrt_tms = uint16(5, writable=True, unit='Secs')
    """RvrtTms. Timeout period for volt-VAR curve selection."""

    rmp_tms = uint16(6, writable=True, unit='Secs')
    """RmpTms. The time of the PT1 in seconds (time to accomplish a change of 95%)."""

    n_crv = uint16(7)
    """NCrv. Number of curves supported (recommend 4)."""

    n_pt = uint16(8)
    """NPt. Number of curve points supported (maximum of 20)."""

    # 'curve' repeats to fill the model length and defines no count
    # point; size it from the scanned model.length:
    # curve = repeating_group(N, VoltVarCurve, stride=54)


class LvrtCurve(Component):
    """One 'curve' block of SunSpec model 129."""

    act_pt = uint16(12, writable=True)
    """ActPt. Number of active points in array."""

    tms1 = uint16(13, scale_register=9, writable=True, unit='Secs')
    """Tms1. Point 1 must disconnect duration."""

    v1 = uint16(14, scale_register=10, writable=True, unit='% VRef')
    """V1. Point 1 must disconnect voltage."""

    tms2 = uint16(15, scale_register=9, writable=True, unit='Secs')
    """Tms2. Point 2 must disconnect duration."""

    v2 = uint16(16, scale_register=10, writable=True, unit='% VRef')
    """V2. Point 2 must disconnect voltage."""

    tms3 = uint16(17, scale_register=9, writable=True, unit='Secs')
    """Tms3. Point 3 must disconnect duration."""

    v3 = uint16(18, scale_register=10, writable=True, unit='% VRef')
    """V3. Point 3 must disconnect voltage."""

    tms4 = uint16(19, scale_register=9, writable=True, unit='Secs')
    """Tms4. Point 4 must disconnect duration."""

    v4 = uint16(20, scale_register=10, writable=True, unit='% VRef')
    """V4. Point 4 must disconnect voltage."""

    tms5 = uint16(21, scale_register=9, writable=True, unit='Secs')
    """Tms5. Point 5 must disconnect duration."""

    v5 = uint16(22, scale_register=10, writable=True, unit='% VRef')
    """V5. Point 5 must disconnect voltage."""

    tms6 = uint16(23, scale_register=9, writable=True, unit='Secs')
    """Tms6. Point 6 must disconnect duration."""

    v6 = uint16(24, scale_register=10, writable=True, unit='% VRef')
    """V6. Point 6 must disconnect voltage."""

    tms7 = uint16(25, scale_register=9, writable=True, unit='Secs')
    """Tms7. Point 7 must disconnect duration."""

    v7 = uint16(26, scale_register=10, writable=True, unit='% VRef')
    """V7. Point 7 must disconnect voltage."""

    tms8 = uint16(27, scale_register=9, writable=True, unit='Secs')
    """Tms8. Point 8 must disconnect duration."""

    v8 = uint16(28, scale_register=10, writable=True, unit='% VRef')
    """V8. Point 8 must disconnect voltage."""

    tms9 = uint16(29, scale_register=9, writable=True, unit='Secs')
    """Tms9. Point 9 must disconnect duration."""

    v9 = uint16(30, scale_register=10, writable=True, unit='% VRef')
    """V9. Point 9 must disconnect voltage."""

    tms10 = uint16(31, scale_register=9, writable=True, unit='Secs')
    """Tms10. Point 10 must disconnect duration."""

    v10 = uint16(32, scale_register=10, writable=True, unit='% VRef')
    """V10. Point 10 must disconnect voltage."""

    tms11 = uint16(33, scale_register=9, writable=True, unit='Secs')
    """Tms11. Point 11 must disconnect duration."""

    v11 = uint16(34, scale_register=10, writable=True, unit='% VRef')
    """V11. Point 11 must disconnect voltage."""

    tms12 = uint16(35, scale_register=9, writable=True, unit='Secs')
    """Tms12. Point 12 must disconnect duration."""

    v12 = uint16(36, scale_register=10, writable=True, unit='% VRef')
    """V12. Point 12 must disconnect voltage."""

    tms13 = uint16(37, scale_register=9, writable=True, unit='Secs')
    """Tms13. Point 13 must disconnect duration."""

    v13 = uint16(38, scale_register=10, writable=True, unit='% VRef')
    """V13. Point 13 must disconnect voltage."""

    tms14 = uint16(39, scale_register=9, writable=True, unit='Secs')
    """Tms14. Point 14 must disconnect duration."""

    v14 = uint16(40, scale_register=10, writable=True, unit='% VRef')
    """V14. Point 14 must disconnect voltage."""

    tms15 = uint16(41, scale_register=9, writable=True, unit='Secs')
    """Tms15. Point 15 must disconnect duration."""

    v15 = uint16(42, scale_register=10, writable=True, unit='% VRef')
    """V15. Point 15 must disconnect voltage."""

    tms16 = uint16(43, scale_register=9, writable=True, unit='Secs')
    """Tms16. Point 16 must disconnect duration."""

    v16 = uint16(44, scale_register=10, writable=True, unit='% VRef')
    """V16. Point 16 must disconnect voltage."""

    tms17 = uint16(45, scale_register=9, writable=True, unit='Secs')
    """Tms17. Point 17 must disconnect duration."""

    v17 = uint16(46, scale_register=10, writable=True, unit='% VRef')
    """V17. Point 17 must disconnect voltage."""

    tms18 = uint16(47, scale_register=9, writable=True, unit='Secs')
    """Tms18. Point 18 must disconnect duration."""

    v18 = uint16(48, scale_register=10, writable=True, unit='% VRef')
    """V18. Point 18 must disconnect voltage."""

    tms19 = uint16(49, scale_register=9, writable=True, unit='Secs')
    """Tms19. Point 19 must disconnect duration."""

    v19 = uint16(50, scale_register=10, writable=True, unit='% VRef')
    """V19. Point 19 must disconnect voltage."""

    tms20 = uint16(51, scale_register=9, writable=True, unit='Secs')
    """Tms20. Point 20 must disconnect duration."""

    v20 = uint16(52, scale_register=10, writable=True, unit='% VRef')
    """V20. Point 20 must disconnect voltage."""

    crv_nam = string(53, 8, writable=True)
    """CrvNam. Optional description for curve."""

    read_only = enum16(61, ReadOnly)
    """ReadOnly. Curve is read-only or can be modified."""


class Lvrt(SunSpecComponent):
    """SunSpec model 129: LVRTD."""

    act_crv = uint16(2, writable=True)
    """ActCrv. Index of active curve. 0=no active curve."""

    mod_ena = bitfield16(3, ModEna, writable=True)
    """ModEna. LVRT control mode. Enable active curve."""

    win_tms = uint16(4, writable=True, unit='Secs')
    """WinTms. Time window for LVRT change."""

    rvrt_tms = uint16(5, writable=True, unit='Secs')
    """RvrtTms. Timeout period for LVRT curve selection."""

    rmp_tms = uint16(6, writable=True, unit='Secs')
    """RmpTms. Ramp time for moving from current mode to new mode."""

    n_crv = uint16(7)
    """NCrv. Number of curves supported (recommend 4)."""

    n_pt = uint16(8)
    """NPt. Number of curve points supported (maximum of 20)."""

    # 'curve' repeats to fill the model length and defines no count
    # point; size it from the scanned model.length:
    # curve = repeating_group(N, LvrtCurve, stride=50)


class HvrtCurve(Component):
    """One 'curve' block of SunSpec model 130."""

    act_pt = uint16(12, writable=True)
    """ActPt. Number of active points in array."""

    tms1 = uint16(13, scale_register=9, writable=True, unit='Secs')
    """Tms1. Point 1 must disconnect duration."""

    v1 = uint16(14, scale_register=10, writable=True, unit='% VRef')
    """V1. Point 1 must disconnect voltage."""

    tms2 = uint16(15, scale_register=9, writable=True, unit='Secs')
    """Tms2. Point 2 must disconnect duration."""

    v2 = uint16(16, scale_register=10, writable=True, unit='% VRef')
    """V2. Point 2 must disconnect voltage."""

    tms3 = uint16(17, scale_register=9, writable=True, unit='Secs')
    """Tms3. Point 3 must disconnect duration."""

    v3 = uint16(18, scale_register=10, writable=True, unit='% VRef')
    """V3. Point 3 must disconnect voltage."""

    tms4 = uint16(19, scale_register=9, writable=True, unit='Secs')
    """Tms4. Point 4 must disconnect duration."""

    v4 = uint16(20, scale_register=10, writable=True, unit='% VRef')
    """V4. Point 4 must disconnect voltage."""

    tms5 = uint16(21, scale_register=9, writable=True, unit='Secs')
    """Tms5. Point 5 must disconnect duration."""

    v5 = uint16(22, scale_register=10, writable=True, unit='% VRef')
    """V5. Point 5 must disconnect voltage."""

    tms6 = uint16(23, scale_register=9, writable=True, unit='Secs')
    """Tms6. Point 6 must disconnect duration."""

    v6 = uint16(24, scale_register=10, writable=True, unit='% VRef')
    """V6. Point 6 must disconnect voltage."""

    tms7 = uint16(25, scale_register=9, writable=True, unit='Secs')
    """Tms7. Point 7 must disconnect duration."""

    v7 = uint16(26, scale_register=10, writable=True, unit='% VRef')
    """V7. Point 7 must disconnect voltage."""

    tms8 = uint16(27, scale_register=9, writable=True, unit='Secs')
    """Tms8. Point 8 must disconnect duration."""

    v8 = uint16(28, scale_register=10, writable=True, unit='% VRef')
    """V8. Point 8 must disconnect voltage."""

    tms9 = uint16(29, scale_register=9, writable=True, unit='Secs')
    """Tms9. Point 9 must disconnect duration."""

    v9 = uint16(30, scale_register=10, writable=True, unit='% VRef')
    """V9. Point 9 must disconnect voltage."""

    tms10 = uint16(31, scale_register=9, writable=True, unit='Secs')
    """Tms10. Point 10 must disconnect duration."""

    v10 = uint16(32, scale_register=10, writable=True, unit='% VRef')
    """V10. Point 10 must disconnect voltage."""

    tms11 = uint16(33, scale_register=9, writable=True, unit='Secs')
    """Tms11. Point 11 must disconnect duration."""

    v11 = uint16(34, scale_register=10, writable=True, unit='% VRef')
    """V11. Point 11 must disconnect voltage."""

    tms12 = uint16(35, scale_register=9, writable=True, unit='Secs')
    """Tms12. Point 12 must disconnect duration."""

    v12 = uint16(36, scale_register=10, writable=True, unit='% VRef')
    """V12. Point 12 must disconnect voltage."""

    tms13 = uint16(37, scale_register=9, writable=True, unit='Secs')
    """Tms13. Point 13 must disconnect duration."""

    v13 = uint16(38, scale_register=10, writable=True, unit='% VRef')
    """V13. Point 13 must disconnect voltage."""

    tms14 = uint16(39, scale_register=9, writable=True, unit='Secs')
    """Tms14. Point 14 must disconnect duration."""

    v14 = uint16(40, scale_register=10, writable=True, unit='% VRef')
    """V14. Point 14 must disconnect voltage."""

    tms15 = uint16(41, scale_register=9, writable=True, unit='Secs')
    """Tms15. Point 15 must disconnect duration."""

    v15 = uint16(42, scale_register=10, writable=True, unit='% VRef')
    """V15. Point 15 must disconnect voltage."""

    tms16 = uint16(43, scale_register=9, writable=True, unit='Secs')
    """Tms16. Point 16 must disconnect duration."""

    v16 = uint16(44, scale_register=10, writable=True, unit='% VRef')
    """V16. Point 16 must disconnect voltage."""

    tms17 = uint16(45, scale_register=9, writable=True, unit='Secs')
    """Tms17. Point 17 must disconnect duration."""

    v17 = uint16(46, scale_register=10, writable=True, unit='% VRef')
    """V17. Point 17 must disconnect voltage."""

    tms18 = uint16(47, scale_register=9, writable=True, unit='Secs')
    """Tms18. Point 18 must disconnect duration."""

    v18 = uint16(48, scale_register=10, writable=True, unit='% VRef')
    """V18. Point 18 must disconnect voltage."""

    tms19 = uint16(49, scale_register=9, writable=True, unit='Secs')
    """Tms19. Point 19 must disconnect duration."""

    v19 = uint16(50, scale_register=10, writable=True, unit='% VRef')
    """V19. Point 19 must disconnect voltage."""

    tms20 = uint16(51, scale_register=9, writable=True, unit='Secs')
    """Tms20. Point 20 must disconnect duration."""

    v20 = uint16(52, scale_register=10, writable=True, unit='% VRef')
    """V20. Point 20 must disconnect voltage."""

    crv_nam = string(53, 8, writable=True)
    """CrvNam. Optional description for curve."""

    read_only = enum16(61, ReadOnly)
    """ReadOnly. Curve is read-only or can be modified."""


class Hvrt(SunSpecComponent):
    """SunSpec model 130: HVRTD."""

    act_crv = uint16(2, writable=True)
    """ActCrv. Index of active curve. 0=no active curve."""

    mod_ena = bitfield16(3, ModEna, writable=True)
    """ModEna. HVRT control mode. Enable active curve."""

    win_tms = uint16(4, writable=True, unit='Secs')
    """WinTms. Time window for HVRT change."""

    rvrt_tms = uint16(5, writable=True, unit='Secs')
    """RvrtTms. Timeout period for HVRT curve selection."""

    rmp_tms = uint16(6, writable=True, unit='Secs')
    """RmpTms. Ramp time for moving from current mode to new mode."""

    n_crv = uint16(7)
    """NCrv. Number of curves supported (recommend 4)."""

    n_pt = uint16(8)
    """NPt. Number of curve points supported (maximum of 20)."""

    # 'curve' repeats to fill the model length and defines no count
    # point; size it from the scanned model.length:
    # curve = repeating_group(N, HvrtCurve, stride=50)


class VoltWattCurve(Component):
    """One 'curve' block of SunSpec model 132."""

    act_pt = uint16(12, writable=True)
    """ActPt. Number of active points in array."""

    dept_ref = enum16(13, VoltWattCurveDeptRef, writable=True)
    """DeptRef. Defines the meaning of the Watts DeptRef. 1=% WMax 2=% WAvail."""

    v1 = uint16(14, scale_register=9, writable=True, unit='% VRef')
    """V1. Point 1 Volts."""

    w1 = int16(15, scale_register=10, writable=True, unit='% VRef')
    """W1. Point 1 Watts."""

    v2 = uint16(16, scale_register=9, writable=True, unit='% VRef')
    """V2. Point 2 Volts."""

    w2 = int16(17, scale_register=10, writable=True, unit='% VRef')
    """W2. Point 2 Watts."""

    v3 = uint16(18, scale_register=9, writable=True, unit='% VRef')
    """V3. Point 3 Volts."""

    w3 = int16(19, scale_register=10, writable=True, unit='% VRef')
    """W3. Point 3 Watts."""

    v4 = uint16(20, scale_register=9, writable=True, unit='% VRef')
    """V4. Point 4 Volts."""

    w4 = int16(21, scale_register=10, writable=True, unit='% VRef')
    """W4. Point 4 Watts."""

    v5 = uint16(22, scale_register=9, writable=True, unit='% VRef')
    """V5. Point 5 Volts."""

    w5 = int16(23, scale_register=10, writable=True, unit='% VRef')
    """W5. Point 5 Watts."""

    v6 = uint16(24, scale_register=9, writable=True, unit='% VRef')
    """V6. Point 6 Volts."""

    w6 = int16(25, scale_register=10, writable=True, unit='% VRef')
    """W6. Point 6 Watts."""

    v7 = uint16(26, scale_register=9, writable=True, unit='% VRef')
    """V7. Point 7 Volts."""

    w7 = int16(27, scale_register=10, writable=True, unit='% VRef')
    """W7. Point 7 Watts."""

    v8 = uint16(28, scale_register=9, writable=True, unit='% VRef')
    """V8. Point 8 Volts."""

    w8 = int16(29, scale_register=10, writable=True, unit='% VRef')
    """W8. Point 8 Watts."""

    v9 = uint16(30, scale_register=9, writable=True, unit='% VRef')
    """V9. Point 9 Volts."""

    w9 = int16(31, scale_register=10, writable=True, unit='% VRef')
    """W9. Point 9 Watts."""

    v10 = uint16(32, scale_register=9, writable=True, unit='% VRef')
    """V10. Point 10 Volts."""

    w10 = int16(33, scale_register=10, writable=True, unit='% VRef')
    """W10. Point 10 Watts."""

    v11 = uint16(34, scale_register=9, writable=True, unit='% VRef')
    """V11. Point 11 Volts."""

    w11 = int16(35, scale_register=10, writable=True, unit='% VRef')
    """W11. Point 11 Watts."""

    v12 = uint16(36, scale_register=9, writable=True, unit='% VRef')
    """V12. Point 12 Volts."""

    w12 = int16(37, scale_register=10, writable=True, unit='% VRef')
    """W12. Point 12 Watts."""

    v13 = uint16(38, scale_register=9, writable=True, unit='% VRef')
    """V13. Point 13 Volts."""

    w13 = int16(39, scale_register=10, writable=True, unit='% VRef')
    """W13. Point 13 Watts."""

    v14 = uint16(40, scale_register=9, writable=True, unit='% VRef')
    """V14. Point 14 Volts."""

    w14 = int16(41, scale_register=10, writable=True, unit='% VRef')
    """W14. Point 14 Watts."""

    v15 = uint16(42, scale_register=9, writable=True, unit='% VRef')
    """V15. Point 15 Volts."""

    w15 = int16(43, scale_register=10, writable=True, unit='% VRef')
    """W15. Point 15 Watts."""

    v16 = uint16(44, scale_register=9, writable=True, unit='% VRef')
    """V16. Point 16 Volts."""

    w16 = int16(45, scale_register=10, writable=True, unit='% VRef')
    """W16. Point 16 Watts."""

    v17 = uint16(46, scale_register=9, writable=True, unit='% VRef')
    """V17. Point 17 Volts."""

    w17 = int16(47, scale_register=10, writable=True, unit='% VRef')
    """W17. Point 17 Watts."""

    v18 = uint16(48, scale_register=9, writable=True, unit='% VRef')
    """V18. Point 18 Volts."""

    w18 = int16(49, scale_register=10, writable=True, unit='% VRef')
    """W18. Point 18 Watts."""

    v19 = uint16(50, scale_register=9, writable=True, unit='% VRef')
    """V19. Point 19 Volts."""

    w19 = int16(51, scale_register=10, writable=True, unit='% VRef')
    """W19. Point 19 Watts."""

    v20 = uint16(52, scale_register=9, writable=True, unit='% VRef')
    """V20. Point 20 Volts."""

    w20 = int16(53, scale_register=10, writable=True, unit='% VRef')
    """W20. Point 20 Watts."""

    crv_nam = string(54, 8, writable=True)
    """CrvNam. Optional description for curve."""

    rmp_pt1_tms = uint16(62, writable=True, unit='Secs')
    """RmpPt1Tms. The time of the PT1 in seconds (time to accomplish a change of
    95%)."""

    rmp_dec_tmm = uint16(63, scale_register=11, writable=True, unit='% WMax/min')
    """RmpDecTmm. The maximum rate at which the watt value may be reduced in response
    to changes in the voltage value."""

    rmp_inc_tmm = uint16(64, scale_register=11, writable=True, unit='% WMax/min')
    """RmpIncTmm. The maximum rate at which the watt value may be increased in
    response to changes in the voltage value."""

    read_only = enum16(65, ReadOnly)
    """ReadOnly. Curve is read-only or can be modified."""


class VoltWatt(SunSpecComponent):
    """SunSpec model 132: Volt-Watt."""

    act_crv = uint16(2, writable=True)
    """ActCrv. Index of active curve. 0=no active curve."""

    mod_ena = bitfield16(3, ModEna, writable=True)
    """ModEna. Is Volt-Watt control active."""

    win_tms = uint16(4, writable=True, unit='Secs')
    """WinTms. Time window for volt-watt change."""

    rvrt_tms = uint16(5, writable=True, unit='Secs')
    """RvrtTms. Timeout period for volt-watt curve selection."""

    rmp_tms = uint16(6, writable=True, unit='Secs')
    """RmpTms. Ramp time for moving from current mode to new mode."""

    n_crv = uint16(7)
    """NCrv. Number of curves supported (recommend min. 4)."""

    n_pt = uint16(8)
    """NPt. Number of points in array (maximum 20)."""

    # 'curve' repeats to fill the model length and defines no count
    # point; size it from the scanned model.length:
    # curve = repeating_group(N, VoltWattCurve, stride=54)


class LfrtCurve(Component):
    """One 'curve' block of SunSpec model 135."""

    act_pt = uint16(12, writable=True)
    """ActPt. Number of active points in array."""

    tms1 = uint16(13, scale_register=9, writable=True, unit='Secs')
    """Tms1. Point 1 must disconnect duration."""

    hz1 = uint16(14, scale_register=10, writable=True, unit='Hz')
    """Hz1. Point 1 must disconnect frequency."""

    tms2 = uint16(15, scale_register=9, writable=True, unit='Secs')
    """Tms2. Point 2 must disconnect duration."""

    hz2 = uint16(16, scale_register=10, writable=True, unit='Hz')
    """Hz2. Point 2 must disconnect frequency."""

    tms3 = uint16(17, scale_register=9, writable=True, unit='Secs')
    """Tms3. Point 3 must disconnect duration."""

    hz3 = uint16(18, scale_register=10, writable=True, unit='Hz')
    """Hz3. Point 3 must disconnect frequency."""

    tms4 = uint16(19, scale_register=9, writable=True, unit='Secs')
    """Tms4. Point 4 must disconnect duration."""

    hz4 = uint16(20, scale_register=10, writable=True, unit='Hz')
    """Hz4. Point 4 must disconnect frequency."""

    tms5 = uint16(21, scale_register=9, writable=True, unit='Secs')
    """Tms5. Point 5 must disconnect duration."""

    hz5 = uint16(22, scale_register=10, writable=True, unit='Hz')
    """Hz5. Point 5 must disconnect frequency."""

    tms6 = uint16(23, scale_register=9, writable=True, unit='Secs')
    """Tms6. Point 6 must disconnect duration."""

    hz6 = uint16(24, scale_register=10, writable=True, unit='Hz')
    """Hz6. Point 6 must disconnect frequency."""

    tms7 = uint16(25, scale_register=9, writable=True, unit='Secs')
    """Tms7. Point 7 must disconnect duration."""

    hz7 = uint16(26, scale_register=10, writable=True, unit='Hz')
    """Hz7. Point 7 must disconnect frequency."""

    tms8 = uint16(27, scale_register=9, writable=True, unit='Secs')
    """Tms8. Point 8 must disconnect duration."""

    hz8 = uint16(28, scale_register=10, writable=True, unit='Hz')
    """Hz8. Point 8 must disconnect frequency."""

    tms9 = uint16(29, scale_register=9, writable=True, unit='Secs')
    """Tms9. Point 9 must disconnect duration."""

    hz9 = uint16(30, scale_register=10, writable=True, unit='Hz')
    """Hz9. Point 9 must disconnect frequency."""

    tms10 = uint16(31, scale_register=9, writable=True, unit='Secs')
    """Tms10. Point 10 must disconnect duration."""

    hz10 = uint16(32, scale_register=10, writable=True, unit='Hz')
    """Hz10. Point 10 must disconnect frequency."""

    tms11 = uint16(33, scale_register=9, writable=True, unit='Secs')
    """Tms11. Point 11 must disconnect duration."""

    hz11 = uint16(34, scale_register=10, writable=True, unit='Hz')
    """Hz11. Point 11 must disconnect frequency."""

    tms12 = uint16(35, scale_register=9, writable=True, unit='Secs')
    """Tms12. Point 12 must disconnect duration."""

    hz12 = uint16(36, scale_register=10, writable=True, unit='Hz')
    """Hz12. Point 12 must disconnect frequency."""

    tms13 = uint16(37, scale_register=9, writable=True, unit='Secs')
    """Tms13. Point 13 must disconnect duration."""

    hz13 = uint16(38, scale_register=10, writable=True, unit='Hz')
    """Hz13. Point 13 must disconnect frequency."""

    tms14 = uint16(39, scale_register=9, writable=True, unit='Secs')
    """Tms14. Point 14 must disconnect duration."""

    hz14 = uint16(40, scale_register=10, writable=True, unit='Hz')
    """Hz14. Point 14 must disconnect frequency."""

    tms15 = uint16(41, scale_register=9, writable=True, unit='Secs')
    """Tms15. Point 15 must disconnect duration."""

    hz15 = uint16(42, scale_register=10, writable=True, unit='Hz')
    """Hz15. Point 15 must disconnect frequency."""

    tms16 = uint16(43, scale_register=9, writable=True, unit='Secs')
    """Tms16. Point 16 must disconnect duration."""

    hz16 = uint16(44, scale_register=10, writable=True, unit='Hz')
    """Hz16. Point 16 must disconnect frequency."""

    tms17 = uint16(45, scale_register=9, writable=True, unit='Secs')
    """Tms17. Point 17 must disconnect duration."""

    hz17 = uint16(46, scale_register=10, writable=True, unit='Hz')
    """Hz17. Point 17 must disconnect frequency."""

    tms18 = uint16(47, scale_register=9, writable=True, unit='Secs')
    """Tms18. Point 18 must disconnect duration."""

    hz18 = uint16(48, scale_register=10, writable=True, unit='Hz')
    """Hz18. Point 18 must disconnect frequency."""

    tms19 = uint16(49, scale_register=9, writable=True, unit='Secs')
    """Tms19. Point 19 must disconnect duration."""

    hz19 = uint16(50, scale_register=10, writable=True, unit='Hz')
    """Hz19. Point 19 must disconnect frequency."""

    tms20 = uint16(51, scale_register=9, writable=True, unit='Secs')
    """Tms20. Point 20 must disconnect duration."""

    hz20 = uint16(52, scale_register=10, writable=True, unit='Hz')
    """Hz20. Point 20 must disconnect frequency."""

    crv_nam = string(53, 8, writable=True)
    """CrvNam. Optional description for curve."""

    read_only = enum16(61, ReadOnly)
    """ReadOnly. Curve is read-only or can be modified."""


class Lfrt(SunSpecComponent):
    """SunSpec model 135: LFRT."""

    act_crv = uint16(2, writable=True)
    """ActCrv. Index of active curve. 0=no active curve."""

    mod_ena = bitfield16(3, ModEna, writable=True)
    """ModEna. LHzRT control mode. Enable active curve."""

    win_tms = uint16(4, writable=True, unit='Secs')
    """WinTms. Time window for LFRT change."""

    rvrt_tms = uint16(5, writable=True, unit='Secs')
    """RvrtTms. Timeout period for LFRT curve selection."""

    rmp_tms = uint16(6, writable=True, unit='Secs')
    """RmpTms. Ramp time for moving from current mode to new mode."""

    n_crv = uint16(7)
    """NCrv. Number of curves supported (recommend 4)."""

    n_pt = uint16(8)
    """NPt. Number of curve points supported (maximum of 20)."""

    # 'curve' repeats to fill the model length and defines no count
    # point; size it from the scanned model.length:
    # curve = repeating_group(N, LfrtCurve, stride=50)


class HfrtCurve(Component):
    """One 'curve' block of SunSpec model 136."""

    act_pt = uint16(12, writable=True)
    """ActPt. Number of active points in array."""

    tms1 = uint16(13, scale_register=9, writable=True, unit='Secs')
    """Tms1. Point 1 must disconnect duration."""

    hz1 = uint16(14, scale_register=10, writable=True, unit='Hz')
    """Hz1. Point 1 must disconnect frequency."""

    tms2 = uint16(15, scale_register=9, writable=True, unit='Secs')
    """Tms2. Point 2 must disconnect duration."""

    hz2 = uint16(16, scale_register=10, writable=True, unit='Hz')
    """Hz2. Point 2 must disconnect frequency."""

    tms3 = uint16(17, scale_register=9, writable=True, unit='Secs')
    """Tms3. Point 3 must disconnect duration."""

    hz3 = uint16(18, scale_register=10, writable=True, unit='Hz')
    """Hz3. Point 3 must disconnect frequency."""

    tms4 = uint16(19, scale_register=9, writable=True, unit='Secs')
    """Tms4. Point 4 must disconnect duration."""

    hz4 = uint16(20, scale_register=10, writable=True, unit='Hz')
    """Hz4. Point 4 must disconnect frequency."""

    tms5 = uint16(21, scale_register=9, writable=True, unit='Secs')
    """Tms5. Point 5 must disconnect duration."""

    hz5 = uint16(22, scale_register=10, writable=True, unit='Hz')
    """Hz5. Point 5 must disconnect frequency."""

    tms6 = uint16(23, scale_register=9, writable=True, unit='Secs')
    """Tms6. Point 6 must disconnect duration."""

    hz6 = uint16(24, scale_register=10, writable=True, unit='Hz')
    """Hz6. Point 6 must disconnect frequency."""

    tms7 = uint16(25, scale_register=9, writable=True, unit='Secs')
    """Tms7. Point 7 must disconnect duration."""

    hz7 = uint16(26, scale_register=10, writable=True, unit='Hz')
    """Hz7. Point 7 must disconnect frequency."""

    tms8 = uint16(27, scale_register=9, writable=True, unit='Secs')
    """Tms8. Point 8 must disconnect duration."""

    hz8 = uint16(28, scale_register=10, writable=True, unit='Hz')
    """Hz8. Point 8 must disconnect frequency."""

    tms9 = uint16(29, scale_register=9, writable=True, unit='Secs')
    """Tms9. Point 9 must disconnect duration."""

    hz9 = uint16(30, scale_register=10, writable=True, unit='Hz')
    """Hz9. Point 9 must disconnect frequency."""

    tms10 = uint16(31, scale_register=9, writable=True, unit='Secs')
    """Tms10. Point 10 must disconnect duration."""

    hz10 = uint16(32, scale_register=10, writable=True, unit='Hz')
    """Hz10. Point 10 must disconnect frequency."""

    tms11 = uint16(33, scale_register=9, writable=True, unit='Secs')
    """Tms11. Point 11 must disconnect duration."""

    hz11 = uint16(34, scale_register=10, writable=True, unit='Hz')
    """Hz11. Point 11 must disconnect frequency."""

    tms12 = uint16(35, scale_register=9, writable=True, unit='Secs')
    """Tms12. Point 12 must disconnect duration."""

    hz12 = uint16(36, scale_register=10, writable=True, unit='Hz')
    """Hz12. Point 12 must disconnect frequency."""

    tms13 = uint16(37, scale_register=9, writable=True, unit='Secs')
    """Tms13. Point 13 must disconnect duration."""

    hz13 = uint16(38, scale_register=10, writable=True, unit='Hz')
    """Hz13. Point 13 must disconnect frequency."""

    tms14 = uint16(39, scale_register=9, writable=True, unit='Secs')
    """Tms14. Point 14 must disconnect duration."""

    hz14 = uint16(40, scale_register=10, writable=True, unit='Hz')
    """Hz14. Point 14 must disconnect frequency."""

    tms15 = uint16(41, scale_register=9, writable=True, unit='Secs')
    """Tms15. Point 15 must disconnect duration."""

    hz15 = uint16(42, scale_register=10, writable=True, unit='Hz')
    """Hz15. Point 15 must disconnect frequency."""

    tms16 = uint16(43, scale_register=9, writable=True, unit='Secs')
    """Tms16. Point 16 must disconnect duration."""

    hz16 = uint16(44, scale_register=10, writable=True, unit='Hz')
    """Hz16. Point 16 must disconnect frequency."""

    tms17 = uint16(45, scale_register=9, writable=True, unit='Secs')
    """Tms17. Point 17 must disconnect duration."""

    hz17 = uint16(46, scale_register=10, writable=True, unit='Hz')
    """Hz17. Point 17 must disconnect frequency."""

    tms18 = uint16(47, scale_register=9, writable=True, unit='Secs')
    """Tms18. Point 18 must disconnect duration."""

    hz18 = uint16(48, scale_register=10, writable=True, unit='Hz')
    """Hz18. Point 18 must disconnect frequency."""

    tms19 = uint16(49, scale_register=9, writable=True, unit='Secs')
    """Tms19. Point 19 must disconnect duration."""

    hz19 = uint16(50, scale_register=10, writable=True, unit='Hz')
    """Hz19. Point 19 must disconnect frequency."""

    tms20 = uint16(51, scale_register=9, writable=True, unit='Secs')
    """Tms20. Point 20 must disconnect duration."""

    hz20 = uint16(52, scale_register=10, writable=True, unit='Hz')
    """Hz20. Point 20 must disconnect frequency."""

    crv_nam = string(53, 8, writable=True)
    """CrvNam. Optional description for curve."""

    read_only = enum16(61, ReadOnly)
    """ReadOnly. Curve is read-only or can be modified."""


class Hfrt(SunSpecComponent):
    """SunSpec model 136: HFRT."""

    act_crv = uint16(2, writable=True)
    """ActCrv. Index of active curve. 0=no active curve."""

    mod_ena = bitfield16(3, ModEna, writable=True)
    """ModEna. HFRT control mode. Enable active curve."""

    win_tms = uint16(4, writable=True, unit='Secs')
    """WinTms. Time window for HFRT change."""

    rvrt_tms = uint16(5, writable=True, unit='Secs')
    """RvrtTms. Timeout period for HFRT curve selection."""

    rmp_tms = uint16(6, writable=True, unit='Secs')
    """RmpTms. Ramp time for moving from current mode to new mode."""

    n_crv = uint16(7)
    """NCrv. Number of curves supported (recommend 4)."""

    n_pt = uint16(8)
    """NPt. Number of curve points supported (maximum of 20)."""

    # 'curve' repeats to fill the model length and defines no count
    # point; size it from the scanned model.length:
    # curve = repeating_group(N, HfrtCurve, stride=50)


class MpptModule(Component):
    """One 'module' block of SunSpec model 160."""

    id = uint16(10)
    """Input ID."""

    id_str = string(11, 8)
    """Input ID String."""

    dca = uint16(19, scale_register=2, unit='A')
    """DC Current."""

    dcv = uint16(20, scale_register=3, unit='V')
    """DC Voltage."""

    dcw = uint16(21, scale_register=4, unit='W')
    """DC Power."""

    dcwh = acc32(22, scale_register=5, unit='Wh')
    """Lifetime Energy."""

    tms = uint32(24, unit='Secs')
    """Timestamp."""

    tmp = int16(26, unit='C')
    """Temperature."""

    dc_st = enum16(27, MpptModuleOperatingState)
    """Operating State."""

    dc_evt = bitfield32(28, ModuleEvents)
    """Module Events."""


class Mppt(SunSpecComponent):
    """SunSpec model 160: Multiple MPPT Inverter Extension Model."""

    evt = bitfield32(6, GlobalEvents)
    """Global Events."""

    n = uint16(8)
    """Number of Modules."""

    tms_per = uint16(9)
    """Timestamp Period."""

    module = repeating_group(uint16(8), MpptModule, stride=20)
