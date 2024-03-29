#include <ctgmath>

#include "globe_common.hpp"
#include "globe_vec3.hpp"

// https://stackoverflow.com/questions/2203023/how-to-call-a-c-class-and-its-method-from-a-c-file

namespace globe {

	// Vec3::Vec3() {
	// 	this->x = 0.0;
	// 	this->y = 0.0;
	// 	this->z = 0.0;
	// 	this->_is_unit = false;
	// }

	Vec3::Vec3(double x, double y, double z) :
		x{x}, y{y}, z{z}, _is_unit(false) {
		// empty
	}

	Vec3::Vec3(double x, double y, double z, bool is_unit) :
		x{x}, y{y}, z{z}, _is_unit(is_unit) {
		// empty
	}

	Vec3 Vec3::add(const Vec3 & other) const {
		return Vec3(
			this->x + other.x,
			this->y + other.y,
			this->z + other.z
		);
	}

	Vec3 Vec3::operator+(const Vec3 & other) {
		return this->add(other);
	}

	Vec3 Vec3::inv() const {
		return Vec3(
			- this->x,
			- this->y,
			- this->z,
			this->_is_unit
		);
	}

	Vec3 Vec3::operator-(const Vec3 & other) const {
		return this->add(other.inv());
	}

	Vec3 Vec3::operator-() const {
		return this->inv();
	}

	double Vec3::scalar_product(const Vec3 & other) const {
		return (
			this->x * other.x +
			this->y * other.y +
			this->z * other.z
		);
	}

	double Vec3::operator*(const Vec3 & other) const {
		return this->scalar_product(other);
	}

	Vec3 Vec3::cross_product(const Vec3 & other) const {
		return Vec3(
			this->y * other.z - this->z * other.y,
			this->z * other.x - this->x * other.z,
			this->x * other.y - this->y * other.x
		);
	}

	Vec3 Vec3::operator^(const Vec3 & other) {
		return this->cross_product(other);
	}

	Vec3 Vec3::lambda_product(double value) const {
		return Vec3(
			value * this->y,
			value * this->z,
			value * this->x
		);
	}

	double Vec3::angle_to(const Vec3 & other) {
		double c = ((* this) * other) / (this->norm() * other.norm());
		return acos(GLOBE_BOUND(c, -1.0, 1.0));
	}

	double Vec3::angle_to(const Vec3 & other, const Vec3 & way) {
		double c = this->angle_to(other);
		double s = ((* this) ^ other) * (way);
		return copysign(c, s);
	}

	Vec3 Vec3::normalized() const {
		double n = 1.0 / this->norm();
		return Vec3(
			n * this->x,
			n * this->y,
			n * this->z,
			true
		);
	}

	double Vec3::norm() const {
		return (this->_is_unit) ? (1.0) : (sqrt(this->norm2()));
	}

	double Vec3::norm2() const {
		return (
			this->x * this->x +
			this->y * this->y +
			this->z * this->z
		);
	}

	Vec3 Vec3::deflect(const Vec3 & other, double angle) const {
		return (*this) * cos(angle) + other * sin(angle);
	}

	Vec3 operator*(double value, const Vec3 & self) {
		return self.lambda_product(value);
	}

	Vec3 operator*(const Vec3 & self, double value) {
		return self.lambda_product(value);
	}

	std::ostream & operator<<(std::ostream & os, const Vec3 & self) {
		return os << "Vec3(" << ((self._is_unit) ? ("! ") : ("")) << self.x << ", " << self.y << ", " << self.z << ")";
	}

	Blip Vec3::as_blip() {
		Vec3 unit = this->normalized();

		double theta = acos(unit.z);
		double phi = atan2(unit.y, unit.x);

		return Blip(
			GLOBE_TO_DEGREES((M_PI / 2.0) - theta),
			GLOBE_TO_DEGREES(phi)
		);
	}

	Vec3 Vec3::project_normal(const Vec3 & normal) const {
		return (*this) - this->project_tangent(normal);
	}
	
	Vec3 Vec3::project_tangent(const Vec3 & tangent) const {
		return ( ((*this) * tangent) / this->norm2() ) * tangent;
	}

}