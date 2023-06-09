#!/usr/bin/env zsh

pushd build
	rm *.o
	rm *.exe
popd

for file in src/*.c
do
	echo "$file -> build/${file:t:r}.o"
	gcc -std=c99 -Iinclude -c $file -o build/${file:t:r}.o
done

for file in test/*.c
do
	echo "$file -> build/${file:t:r}.exe"
	gcc -std=c99 -save-temps -Iinclude build/*.o $file -lm -o build/${file:t:r}.exe 
	pushd test
		../build/${file:t:r}.exe
	popd
done
