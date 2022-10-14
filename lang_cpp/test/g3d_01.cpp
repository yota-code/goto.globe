#include <iostream>

#include "globe.hpp"

int main(int argc, char * argv[]) {

	auto u = globe::Vec3(0.0, 2.0, 1.0);
	auto v = globe::Vec3(2.0, -1.0, 0.0);
	double k = 3.0;

	std::cout << "u.add(v) :: " << u.add(v) << std::endl;
	std::cout << "u + v :: " << (u + v) << std::endl;
	std::cout << "u.inv() :: " << u.inv() << std::endl;
	std::cout << "-u :: " << (-u) << std::endl;
	std::cout << "u.scalar_product(v) :: " << u.scalar_product(v) << std::endl;
	std::cout << "u * v :: " << (u * v) << std::endl;
	std::cout << "u.cross_product(v) :: " << u.cross_product(v) << std::endl;
	std::cout << "u ^ v :: " << (u ^ v) << std::endl;
	std::cout << "u - v :: " << (u - v) << std::endl;
	std::cout << "u.lambda_product(k) :: " << u.lambda_product(k) << std::endl;
	std::cout << "k * v :: " << (k * v) << std::endl;
	std::cout << "v * k :: " << (v * k) << std::endl;
	std::cout << "u.norm() :: " << (u.norm()) << std::endl;
	std::cout << "u.normalized() :: " << (u.normalized()) << std::endl;

}
