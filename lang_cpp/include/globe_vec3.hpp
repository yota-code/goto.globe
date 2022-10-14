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

			Vec3(double x, double y, double z);
			Vec3(double x, double y, double z, bool is_unit);

			Blip to_blip();

			Vec3 cross_product(const Vec3 & other);
			Vec3 lambda_product(double value);
			double scalar_product(const Vec3 & other);

			Vec3 add(const Vec3 & other); // return the sum of two vectors
			Vec3 inv(); // return the additive inverse of a vector

			Vec3 normalized();

			double norm();
			double norm2();

			double angle_to(Vec3 & other);
			double angle_to(Vec3 & other, Vec3 & way);

			Vec3 operator+(const Vec3 & other); // overload + with add()
			Vec3 operator-(Vec3 & other); // overload - with add() of inv()
			Vec3 operator-(); // overload -u with u.inv()
			double operator*(const Vec3 & other); // overload * with scalar_product()
			Vec3 operator^(const Vec3 & other); // overload ^ with cross_product()

			friend Vec3 operator*(double k, Vec3 & self);
			friend Vec3 operator*(Vec3 & self, double k);

			friend std::ostream & operator<<(std::ostream & os, const Vec3 & self);

		private :

			bool _is_unit;

	};


}

#endif /* INCLUDE_globe_vec3_H */