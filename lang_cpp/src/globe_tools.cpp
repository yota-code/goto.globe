#include <ctgmath>

#include "globe_common.hpp"
#include "globe_line.hpp"

#include "globe_tools.hpp"

namespace globe {

	Arc turn_3pt(const Vec3 & A, const Vec3 & B, const Vec3 & C, double radius) {

		double aperture = radius / GLOBE_EARTH_RADIUS;

		Line line1 = Line(B, A);
		Line line2 = Line(B, C);

		double q = line1.Az.angle_to(line2.Az, line1.Ax); // angle between BA and BC
		Vec3 Q = (line1.Az + line2.Az).normalized(); // vector which goes in between the segments BA and BC

		double w = copysign(1.0, q);

		Vec3 P = line1.Bx; // first point
		Vec3 R = line1.Ax; // second point, at the summit of the angle

		// the demonstration of this result should be in a notebook
		double r = -(pow(P * Q, 2)) / (
			P.y*P.y*(-1+R.y*R.y) +
			2*P.x*P.z*R.x*R.z +
			2*P.y*R.y*(P.x*R.x+P.z*R.z) +
			P.z*P.z*(-1+R.z*R.z) -
			P.x*P.x*(R.y*R.y+R.z*R.z)
		);

		double t = acos(sqrt(pow(cos(aperture), 2) - r) / sqrt(1 - r));

		Vec3 V = R.deflect(Q, t);

		Vec3 E = V.project_normal(line1.Ay).normalized();
		Vec3 F = V.project_normal(line2.Ay).normalized();

		double angle_VE = V.angle_to(E);
		double angle_VF = V.angle_to(F);

		return Arc(E, F, copysign((angle_VE + angle_VF) / 2.0, w), false);
		// TODO, ça pourrait être un large arc sous certaines conditions... vérifier

	}

	/*Arc turn_4pt(const Vec3 & A, const Vec3 & B, const Vec3 & C, const Vec3 & D) {






	}*/

	double turn_angle(const Vec3 & A, const Vec3 & B, const Vec3 & C) {
		// return the angle the helicopter have to turn in B, to go from AB to BC
		Line line1 = Line(B, A);
		Line line2 = Line(B, C);

		return line2.Az.angle_to(- line1.Az, B);
	}


}