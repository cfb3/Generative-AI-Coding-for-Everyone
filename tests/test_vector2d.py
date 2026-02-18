"""Tests for skunk.physics.vector2d.Vector2D."""

import math
import pytest
from skunk.physics.vector2d import Vector2D


class TestArithmetic:
    def test_add(self):
        assert Vector2D(1, 2) + Vector2D(3, 4) == Vector2D(4, 6)

    def test_sub(self):
        assert Vector2D(5, 7) - Vector2D(2, 3) == Vector2D(3, 4)

    def test_mul_scalar(self):
        assert Vector2D(2, 3) * 4 == Vector2D(8, 12)

    def test_rmul_scalar(self):
        assert 4 * Vector2D(2, 3) == Vector2D(8, 12)

    def test_truediv(self):
        assert Vector2D(6, 9) / 3 == Vector2D(2, 3)

    def test_truediv_by_zero_raises(self):
        with pytest.raises(ZeroDivisionError):
            Vector2D(1, 1) / 0

    def test_neg(self):
        assert -Vector2D(3, -4) == Vector2D(-3, 4)

    def test_add_identity(self):
        v = Vector2D(5, -3)
        assert v + Vector2D(0, 0) == v

    def test_sub_self_is_zero(self):
        v = Vector2D(7, 11)
        assert v - v == Vector2D(0, 0)

    def test_mul_by_zero(self):
        assert Vector2D(99, -42) * 0 == Vector2D(0, 0)

    def test_mul_by_negative(self):
        assert Vector2D(2, 3) * -1 == Vector2D(-2, -3)


class TestMagnitude:
    def test_unit_x(self):
        assert Vector2D(1, 0).magnitude == 1.0

    def test_3_4_5_triangle(self):
        assert Vector2D(3, 4).magnitude == pytest.approx(5.0)

    def test_zero_vector(self):
        assert Vector2D(0, 0).magnitude == 0.0

    def test_magnitude_sq(self):
        assert Vector2D(3, 4).magnitude_sq == pytest.approx(25.0)

    def test_magnitude_sq_avoids_sqrt(self):
        v = Vector2D(3, 4)
        assert v.magnitude_sq == pytest.approx(v.magnitude ** 2)

    def test_negative_components(self):
        assert Vector2D(-3, -4).magnitude == pytest.approx(5.0)


class TestNormalize:
    def test_unit_vector_magnitude(self):
        n = Vector2D(3, 4).normalized()
        assert n.magnitude == pytest.approx(1.0)

    def test_unit_vector_direction(self):
        n = Vector2D(3, 4).normalized()
        assert n.x == pytest.approx(3 / 5)
        assert n.y == pytest.approx(4 / 5)

    def test_zero_vector_returns_zero(self):
        assert Vector2D(0, 0).normalized() == Vector2D(0, 0)

    def test_already_unit(self):
        v = Vector2D(1, 0).normalized()
        assert v == Vector2D(1.0, 0.0)


class TestDot:
    def test_perpendicular_is_zero(self):
        assert Vector2D(1, 0).dot(Vector2D(0, 1)) == 0.0

    def test_parallel_same_direction(self):
        assert Vector2D(2, 0).dot(Vector2D(3, 0)) == pytest.approx(6.0)

    def test_parallel_opposite_direction(self):
        assert Vector2D(2, 0).dot(Vector2D(-3, 0)) == pytest.approx(-6.0)

    def test_general_case(self):
        assert Vector2D(1, 2).dot(Vector2D(3, 4)) == pytest.approx(11.0)

    def test_self_dot_is_magnitude_sq(self):
        v = Vector2D(3, 4)
        assert v.dot(v) == pytest.approx(v.magnitude_sq)


class TestAngle:
    def test_positive_x(self):
        assert Vector2D(1, 0).angle_rad() == pytest.approx(0.0)

    def test_positive_y(self):
        assert Vector2D(0, 1).angle_rad() == pytest.approx(math.pi / 2)

    def test_negative_x(self):
        assert Vector2D(-1, 0).angle_rad() == pytest.approx(math.pi)

    def test_angle_deg(self):
        assert Vector2D(0, 1).angle_deg() == pytest.approx(90.0)


class TestFromAngle:
    def test_zero_angle(self):
        v = Vector2D.from_angle(0.0, 5.0)
        assert v.x == pytest.approx(5.0)
        assert v.y == pytest.approx(0.0)

    def test_90_degrees(self):
        v = Vector2D.from_angle(math.pi / 2, 3.0)
        assert v.x == pytest.approx(0.0, abs=1e-10)
        assert v.y == pytest.approx(3.0)

    def test_default_magnitude_is_one(self):
        v = Vector2D.from_angle(0.0)
        assert v.magnitude == pytest.approx(1.0)

    def test_roundtrip_angle(self):
        angle = 1.23
        v = Vector2D.from_angle(angle, 5.0)
        assert v.angle_rad() == pytest.approx(angle)


class TestClamped:
    def test_under_limit_unchanged(self):
        v = Vector2D(1, 1)
        assert v.clamped(10.0) == v

    def test_over_limit_scaled_down(self):
        v = Vector2D(30, 40)  # magnitude = 50
        c = v.clamped(5.0)
        assert c.magnitude == pytest.approx(5.0)
        # Direction preserved
        assert c.x / c.y == pytest.approx(v.x / v.y)

    def test_exactly_at_limit(self):
        v = Vector2D(3, 4)  # magnitude = 5
        assert v.clamped(5.0) == v

    def test_zero_vector_clamped(self):
        v = Vector2D(0, 0)
        assert v.clamped(5.0) == v


class TestDistanceTo:
    def test_same_point(self):
        v = Vector2D(3, 4)
        assert v.distance_to(v) == 0.0

    def test_known_distance(self):
        a = Vector2D(0, 0)
        b = Vector2D(3, 4)
        assert a.distance_to(b) == pytest.approx(5.0)

    def test_symmetric(self):
        a = Vector2D(1, 2)
        b = Vector2D(4, 6)
        assert a.distance_to(b) == pytest.approx(b.distance_to(a))

    def test_distance_sq(self):
        a = Vector2D(0, 0)
        b = Vector2D(3, 4)
        assert a.distance_sq_to(b) == pytest.approx(25.0)


class TestImmutability:
    def test_frozen(self):
        v = Vector2D(1, 2)
        with pytest.raises(AttributeError):
            v.x = 99

    def test_hashable(self):
        v = Vector2D(1, 2)
        {v: "test"}  # should not raise


class TestRepr:
    def test_repr_format(self):
        r = repr(Vector2D(1.5, -2.3))
        assert "1.500" in r
        assert "-2.300" in r
