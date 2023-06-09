#ifndef INCLUDE_globe_vec3_H
#define INCLUDE_globe_vec3_H

#include <iostream>

#include "globe_blip.hpp"

namespace globe {

	class Blip;

	class Vec3 {

		public :

			double x;
			double y;
			double z;
			
			// Vec3();
			Vec3(double x=0.0, double y=0.0, double z=0.0);
			Vec3(double x, double y, double z, bool is_unit);

			Blip as_blip();

			Vec3 cross_product(const Vec3 & other) const;
			Vec3 lambda_product(double value) const;
			double scalar_product(const Vec3 & other) const;

			Vec3 add(const Vec3 & other) const; // return the sum of two vectors
			Vec3 inv() const; // return the additive inverse of a vector

			Vec3 normalized() const;

			double norm() const;
			double norm2() const;

			double angle_to(const Vec3 & other);
			double angle_to(const Vec3 & other, const Vec3 & way);

			Vec3 deflect(const Vec3 & other, double angle) const;

			Vec3 project_normal(const Vec3 & normal) const;
			Vec3 project_tangent(const Vec3 & tangent) const;

			Vec3 operator+(const Vec3 & other) ; // overload a + b with a.add(b)
			Vec3 operator-(const Vec3 & other) const; // overload a - b with a.add(b.inv())
			Vec3 operator-() const; // overload -u with u.inv()

			double operator*(const Vec3 & other) const; // overload a * b with a.scalar_product(b)
			Vec3 operator^(const Vec3 & other); // overload a ^ b with a.cross_product(b)

			friend Vec3 operator*(double k, const Vec3 & self);
			friend Vec3 operator*(const Vec3 & self, double k);

			friend std::ostream & operator<<(std::ostream & os, const Vec3 & self);

		private :

			bool _is_unit;

	};


}

#endif /* INCLUDE_globe_vec3_H */