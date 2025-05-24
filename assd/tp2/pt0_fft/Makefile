# this Makefile is just for the test the main_test.c exec

CC = gcc
CFLAGS = -std=c11 -Wall -Wextra -O2 -march=native -g
LDLIBS = -lm

SOURCES = fft.c main_test.c
OBJECTS = $(SOURCES:.c=.o)
TARGET = fft_test

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) $(OBJECTS) -o $(TARGET) $(LDLIBS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJECTS) $(TARGET)
