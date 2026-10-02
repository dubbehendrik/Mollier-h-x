import itertools
import math
import pytest
import psychrolib
from thermo import *

psychrolib.SetUnitSystem(psychrolib.SI)


@pytest.mark.parametrize("t,phi,p", [(20,50,950), (30,60,1013.25), (-10,80,950), (0,50,900), (40,20,1100)])
@pytest.mark.parametrize("pair", list(itertools.combinations(KEYS, 2)))
def test_all_ten_input_pairs_recover_state(t, phi, p, pair):
    reference = solve(("T", "phi"), (t,phi), p)
    result = solve(pair, [reference.values()[k] for k in pair], p)
    assert result.T == pytest.approx(t, abs=1e-7)
    assert result.x == pytest.approx(reference.x, abs=1e-7)


@pytest.mark.parametrize("t,phi,p", [(5,30,950), (20,50,950), (30,60,1013.25), (40,20,1100)])
def test_reference_psychrolib(t, phi, p):
    s = solve(("T", "phi"), (t,phi), p)
    w = psychrolib.GetHumRatioFromRelHum(t,phi/100,p*100)
    assert s.x == pytest.approx(1000*w, rel=1e-9)
    assert s.h == pytest.approx(psychrolib.GetMoistAirEnthalpy(t,w)/1000, rel=1e-9)
    assert s.rho == pytest.approx(psychrolib.GetMoistAirDensity(t,w,p*100), rel=1e-8)
    if s.dew >= 0:
        assert s.dew == pytest.approx(psychrolib.GetTDewPointFromHumRatio(t,w,p*100), abs=2e-4)
    else:
        # PsychroLib returns the ice-reference frost point in this range;
        # our water-reference dew point must instead reproduce vapor pressure.
        assert saturation_pressure(s.dew) == pytest.approx(p*100*w/(.621945+w), rel=1e-8)


def test_winter_uses_water_and_is_continuous():
    # Murphy/Koop at -10 °C: ~286.45 Pa, larger than ice saturation (~259.9 Pa).
    assert saturation_pressure(-10) == pytest.approx(286.45, abs=.2)
    assert saturation_pressure(-1e-7) == pytest.approx(saturation_pressure(1e-7), rel=1e-7)
    a = solve(("T", "phi"), (-10,80),950)
    b = process_target(a,HEAT,20,950)
    assert b.x == a.x
    assert b.phi < a.phi


def test_cooling_reaches_dew_then_follows_saturation():
    a = solve(("T", "phi"), (30,60),950)
    b = process_target(a,COOL,10,950)
    path, water = process_path(a,b,COOL,950)
    assert water == pytest.approx(a.x-b.x)
    assert water > 0
    assert any(s.T == pytest.approx(a.dew, abs=1e-8) for s in path)
    for s in path:
        assert s.phi <= 100
        if s.T > a.dew:
            assert s.x == pytest.approx(a.x)
        else:
            assert s.phi == pytest.approx(100)


def test_rejects_ice_separation_but_allows_cold_dry_cooling():
    a = solve(("T", "phi"), (20,50),950)
    with pytest.raises(ValueError, match="Vereisung"):
        process_target(a,COOL,-5,950)
    dry = solve(("T", "phi"), (0,10),950)
    assert process_target(dry,COOL,-10,950).x == dry.x


def test_invalid_and_ambiguous_inputs():
    for pair, values in [(('T','phi'),(20,101)), (('T','x'),(10,20)), (('x','phi'),(0,0)),
                         (('T','T'),(20,20)), (('T','h'),(math.nan,30)), (('T','phi'),(41,30))]:
        with pytest.raises(ValueError):
            solve(pair, values)


def test_process_compatibility_and_pressure():
    a=solve(('T','phi'),(30,60),950)
    b=solve(('T','phi'),(20,50),950)
    with pytest.raises(ValueError, match="Endpunkte"):
        process_path(a,b,COOL,950)
    assert compatible(a,b,950)==[FREE]
    assert solve(('T','phi'),(20,50),950).x > solve(('T','phi'),(20,50),1013.25).x


def test_isenthalpic_humidification():
    a=solve(('T','phi'),(30,10),950)
    b=process_target(a,ISENTHALP,6,950)
    points,_=process_path(a,b,ISENTHALP,950)
    assert all(s.h == pytest.approx(a.h) for s in points)
    assert b.T<a.T


def test_projection_roundtrip():
    for t,x in [(-15,0), (20,8), (40,20)]:
        assert diagram_temperature(diagram_y(t,x),x)==pytest.approx(t)
