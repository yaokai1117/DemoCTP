
include ../makefile.inc


all: 
	$(CXX) $(COMMON_FLAGS) $(INCLUDE) -I$(ROOTPATH)/ctpapi -Wall -c vnctptd.cpp -o vnctptd.o
	$(CXX) $(COMMON_FLAGS) -shared -Wl,-soname,vnctptd.so -o vnctptd.so vnctptd.o -L$(ROOTPATH)/ctpapi  $(LIBRARIES) -l:thosttraderapi.so
	
clean:
	rm *.o *.so
