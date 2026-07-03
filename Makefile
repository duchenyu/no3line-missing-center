CXX = g++
CXXFLAGS = -O3 -march=native -std=c++17 -pthread
LDFLAGS = -pthread
TARGET = no3line

all: $(TARGET)

$(TARGET): no3line.cpp
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)

clean:
	rm -f $(TARGET) result_*.csv

.PHONY: all clean
