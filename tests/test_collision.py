"""Tests for skunk.physics.collision — detection and resolution."""

import pytest
from skunk.physics.vector2d import Vector2D
from skunk.physics.collision import detect_collision, resolve_collision


class TestDetectCollision:
    def test_overlapping_circles(self):
        assert detect_collision(
            Vector2D(0, 0), 10.0,
            Vector2D(15, 0), 10.0,
        ) is True

    def test_non_overlapping_circles(self):
        assert detect_collision(
            Vector2D(0, 0), 10.0,
            Vector2D(25, 0), 10.0,
        ) is False

    def test_barely_touching_not_detected(self):
        # distance == sum of radii → not < so False
        assert detect_collision(
            Vector2D(0, 0), 10.0,
            Vector2D(20, 0), 10.0,
        ) is False

    def test_just_barely_overlapping(self):
        assert detect_collision(
            Vector2D(0, 0), 10.0,
            Vector2D(19.99, 0), 10.0,
        ) is True

    def test_different_radii(self):
        assert detect_collision(
            Vector2D(0, 0), 5.0,
            Vector2D(10, 0), 20.0,
        ) is True

    def test_different_radii_no_overlap(self):
        assert detect_collision(
            Vector2D(0, 0), 5.0,
            Vector2D(30, 0), 10.0,
        ) is False

    def test_same_position(self):
        assert detect_collision(
            Vector2D(5, 5), 1.0,
            Vector2D(5, 5), 1.0,
        ) is True

    def test_diagonal_overlap(self):
        # distance = sqrt(2) ≈ 1.414, sum of radii = 2
        assert detect_collision(
            Vector2D(0, 0), 1.0,
            Vector2D(1, 1), 1.0,
        ) is True


class TestResolveCollision:
    def _total_momentum(self, va, ma, vb, mb):
        return va * ma + vb * mb

    def _total_ke(self, va, ma, vb, mb):
        return 0.5 * ma * va.magnitude_sq + 0.5 * mb * vb.magnitude_sq

    def test_momentum_conserved(self):
        pa, va, ma, ra = Vector2D(0, 0), Vector2D(5, 0), 1.0, 10.0
        pb, vb, mb, rb = Vector2D(15, 0), Vector2D(-3, 0), 1.0, 10.0

        p_before = self._total_momentum(va, ma, vb, mb)
        nva, nvb, _, _ = resolve_collision(pa, va, ma, ra, pb, vb, mb, rb)
        p_after = self._total_momentum(nva, ma, nvb, mb)

        assert p_after.x == pytest.approx(p_before.x, abs=1e-6)
        assert p_after.y == pytest.approx(p_before.y, abs=1e-6)

    def test_energy_conserved(self):
        pa, va, ma, ra = Vector2D(0, 0), Vector2D(5, 0), 1.0, 10.0
        pb, vb, mb, rb = Vector2D(15, 0), Vector2D(-3, 0), 1.0, 10.0

        ke_before = self._total_ke(va, ma, vb, mb)
        nva, nvb, _, _ = resolve_collision(pa, va, ma, ra, pb, vb, mb, rb)
        ke_after = self._total_ke(nva, ma, nvb, mb)

        assert ke_after == pytest.approx(ke_before, rel=1e-6)

    def test_equal_mass_head_on_swap_velocities(self):
        pa, va, ma, ra = Vector2D(0, 0), Vector2D(5, 0), 1.0, 10.0
        pb, vb, mb, rb = Vector2D(15, 0), Vector2D(-5, 0), 1.0, 10.0

        nva, nvb, _, _ = resolve_collision(pa, va, ma, ra, pb, vb, mb, rb)
        assert nva.x == pytest.approx(-5.0, abs=1e-6)
        assert nvb.x == pytest.approx(5.0, abs=1e-6)

    def test_balls_separate_after_collision(self):
        pa, va, ma, ra = Vector2D(0, 0), Vector2D(5, 0), 1.0, 10.0
        pb, vb, mb, rb = Vector2D(15, 0), Vector2D(-3, 0), 1.0, 10.0

        _, _, npa, npb = resolve_collision(pa, va, ma, ra, pb, vb, mb, rb)
        dist = npa.distance_to(npb)
        assert dist >= ra + rb - 0.01  # separated (tiny tolerance)

    def test_already_moving_apart_no_velocity_change(self):
        pa, va, ma, ra = Vector2D(0, 0), Vector2D(-5, 0), 1.0, 10.0
        pb, vb, mb, rb = Vector2D(15, 0), Vector2D(5, 0), 1.0, 10.0

        nva, nvb, _, _ = resolve_collision(pa, va, ma, ra, pb, vb, mb, rb)
        assert nva.x == pytest.approx(va.x)
        assert nvb.x == pytest.approx(vb.x)

    def test_zero_distance_doesnt_crash(self):
        pa = Vector2D(5, 5)
        pb = Vector2D(5, 5)
        va, vb = Vector2D(1, 0), Vector2D(-1, 0)

        nva, nvb, npa, npb = resolve_collision(pa, va, 1.0, 5.0, pb, vb, 1.0, 5.0)
        # Should not crash and should separate
        assert npa.distance_to(npb) > 0

    def test_different_masses_momentum_conserved(self):
        pa, va, ma, ra = Vector2D(0, 0), Vector2D(3, 1), 2.0, 10.0
        pb, vb, mb, rb = Vector2D(15, 0), Vector2D(-1, -1), 5.0, 10.0

        p_before = self._total_momentum(va, ma, vb, mb)
        nva, nvb, _, _ = resolve_collision(pa, va, ma, ra, pb, vb, mb, rb)
        p_after = self._total_momentum(nva, ma, nvb, mb)

        assert p_after.x == pytest.approx(p_before.x, abs=1e-6)
        assert p_after.y == pytest.approx(p_before.y, abs=1e-6)

    def test_different_masses_energy_conserved(self):
        pa, va, ma, ra = Vector2D(0, 0), Vector2D(3, 1), 2.0, 10.0
        pb, vb, mb, rb = Vector2D(15, 0), Vector2D(-1, -1), 5.0, 10.0

        ke_before = self._total_ke(va, ma, vb, mb)
        nva, nvb, _, _ = resolve_collision(pa, va, ma, ra, pb, vb, mb, rb)
        ke_after = self._total_ke(nva, ma, nvb, mb)

        assert ke_after == pytest.approx(ke_before, rel=1e-6)
