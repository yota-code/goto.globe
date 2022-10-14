#ifndef INCLUDE_globe_blip_H
#define INCLUDE_globe_blip_H

#include <iostream>

#include "globe_vec3.hpp"

namespace globe {

	class Vec3;

	class Blip {

		public:

			double lat;
			double lon;

			Blip(double lat, double lon);
			Vec3 to_vec3();

			double distance(Blip & other);

			friend std::ostream & operator<<(std::ostream & os, const Blip & self);

	};

}

#endif /* INCLUDE_globe_blip_H */