echo "Installing......"
export LD_LIBRARY_PATH=$(pwd)/dependency/vnctp/ctpapi:#LD_LIBRARY_PATH
cd dependency/vnctp/
cd vnctpmd/
make
cd ../vnctptd/
make
cd ../../..
cp dependency/vnctp/vnctptd/vnctptd.so .
cp dependency/vnctp/vnctpmd/vnctpmd.so .

python ui.py
