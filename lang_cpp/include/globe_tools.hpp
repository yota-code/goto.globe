#ifndef INCLUDE_globe_tools_H
#define INCLUDE_globe_tools_H

#include "globe_vec3.hpp"

#include "globe_arc.hpp"

namespace globe {

	Arc turn_3pt(const Vec3 & A, const Vec3 & B, const Vec3 & C, double radius);

}

#endif /* INCLUDE_globe_tools_H */
