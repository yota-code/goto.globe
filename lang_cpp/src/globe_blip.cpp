#include <ctgmath>

#include "globe_common.hpp"
#include "globe_blip.hpp"

namespace globe {

	Blip::Blip(double lat, double lon) {
		this->lat = lat;
		this->lon = lon;
	}

	double Blip::distance(Blip & other) {
		Vec3 u = this->to_vec3();
		Vec3 v = other.to_vec3();
		return u.angle_to(v) * GLOBE_EARTH_RADIUS;
	}

	std::ostream & operator<<(std::ostream & os, const Blip & self) {
		return os << "Blip(" << self.lat << ", " << self.lon << ")";
	}

	Vec3 Blip::to_vec3() {
		double theta = M_PI_2 - GLOBE_TO_RADIANS(this->lat);
		double phi = GLOBE_TO_RADIANS(this->lon);

		double sin_theta = sin(theta);
		double cos_theta = cos(theta);

		double sin_phi = sin(phi);
		double cos_phi = cos(phi);

		return Vec3(
			sin_theta * cos_phi,
			sin_theta * sin_phi,
			cos_theta,
			true
		);
	}

}