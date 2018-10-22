# makefile
all: sort
sort: sort.o
	gcc -o $@ $+
sort.o : sort.s
	as -g -mfpu=vfpv2 -o $@ $<
clean:
	rm -vf first *.o
