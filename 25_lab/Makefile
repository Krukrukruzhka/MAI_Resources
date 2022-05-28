FLAGS = -std=c99
H = dequeue.h
SRC = main.c dequeue.c
OBJ = main.o dequeue.o

all: $(OBJ)
	gcc -o main $(OBJ) $(FLAGS)

main.o: $(H)
	gcc $(FLAGS) -c main.c

deque.o: $(H)
	gcc $(FLAGS) -c deque.c

pre:
	gcc -c $(SRC)

clean:
	rm -f main $(OBJ)