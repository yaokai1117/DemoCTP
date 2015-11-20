
include ../makefile.inc


all: 
	$(CXX) $(COMMON_FLAGS) $(INCLUDE) -I$(ROOTPATH)/ctpapi -c vnctpmd.cpp -o vnctpmd.o
	$(CXX) $(COMMON_FLAGS) -shared -Wl,-soname,vnctpmd.so -o vnctpmd.so vnctpmd.o -L$(ROOTPATH)/ctpapi  $(LIBRARIES) -l:thostmduserapi.so -l:thosttraderapi.so
	
clean:
	rm *.o *.so
