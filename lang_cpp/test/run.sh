#!/usr/bin/env zsh

pushd build
	rm *.o
	rm *.exe
popd

for file in src/*.cpp
do
	echo "$file -> build/${file:t:r}.o"
	g++ -std=c++11 -Iinclude -c $file -o build/${file:t:r}.o
done

for file in test/*.cpp
do
	echo "$file -> build/${file:t:r}.exe"
	g++ -std=c++11 -save-temps -Iinclude build/*.o $file -lm -o build/${file:t:r}.exe 
	pushd test
		../build/${file:t:r}.exe
	popd
done
