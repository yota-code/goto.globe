#include <ctgmath>

#include "globe_common.hpp"
#include "globe_vec3.hpp"

// https://stackoverflow.com/questions/2203023/how-to-call-a-c-class-and-its-method-from-a-c-file

namespace globe {

	Vec3::Vec3(double x, double y, double z) {
		this->x = x;
		this->y = y;
		this->z = z;
		this->_is_unit = false;
	}

	Vec3::Vec3(double x, double y, double z, bool is_unit) {
		this->x = x;
		this->y = y;
		this->z = z;
		this->_is_unit = is_unit;
	}

	Vec3 Vec3::add(const Vec3 & other) {
		return Vec3(
			this->x + other.x,
			this->y + other.y,
			this->z + other.z
		);
	}

	Vec3 Vec3::operator+(const Vec3 & other) {
		return this->add(other);
	}

	Vec3 Vec3::inv() {
		return Vec3(
			- this->x,
			- this->y,
			- this->z,
			this->_is_unit
		);
	}

	Vec3 Vec3::operator-(Vec3 & other) {
		return this->add(other.inv());
	}

	Vec3 Vec3::operator-() {
		return this->inv();
	}

	double Vec3::scalar_product(const Vec3 & other) {
		return (
			this->x * other.x +
			this->y * other.y +
			this->z * other.z
		);
	}

	double Vec3::operator*(const Vec3 & other) {
		return this->scalar_product(other);
	}

	Vec3 Vec3::cross_product(const Vec3 & other) {
		return Vec3(
			this->y * other.z - this->z * other.y,
			this->z * other.x - this->x * other.z,
			this->x * other.y - this->y * other.x
		);
	}

	Vec3 Vec3::operator^(const Vec3 & other) {
		return this->cross_product(other);
	}

	Vec3 Vec3::lambda_product(double value) {
		return Vec3(
			value * this->y,
			value * this->z,
			value * this->x
		);
	}

	double Vec3::angle_to(Vec3 & other) {
		double c = ((* this) * other) / (this->norm() * other.norm());
		return acos(GLOBE_BOUND(c, -1.0, 1.0));
	}

	double Vec3::angle_to(Vec3 & other, Vec3 & way) {
		double c = this->angle_to(other);
		double s = ((* this) ^ other) * (way);
		return copysign(c, s);
	}

	Vec3 Vec3::normalized() {
		double n = this->norm();
		return Vec3(
			n * this->x,
			n * this->y,
			n * this->z,
			true
		);
	}

	double Vec3::norm() {
		return (this->_is_unit) ? (1.0) : ( sqrt(this->norm2()) );
	}

	double Vec3::norm2() {
		return (
			this->x * this->x +
			this->y * this->y +
			this->z * this->z
		);
	}

	Vec3 operator*(double value, Vec3 & self) {
		return self.lambda_product(value);
	}

	Vec3 operator*(Vec3 & self, double value) {
		return self.lambda_product(value);
	}

	std::ostream & operator<<(std::ostream & os, const Vec3 & self) {
		return os << "Vec3(" << ((self._is_unit) ? ("= ") : ("")) << self.x << ", " << self.y << ", " << self.z << ")";
	}

	Blip Vec3::to_blip() {
		auto unit = this->normalized();

		double theta = acos(unit.z);
		double phi = atan2(unit.y, unit.x);

		return Blip(
			GLOBE_TO_DEGREES(M_PI_2 - theta),
			GLOBE_TO_DEGREES(phi)
		);
	}

}