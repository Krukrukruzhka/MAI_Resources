#ifndef dequeue_h
#define dequeue_h
#include <stdio.h>
#include "stdlib.h"
#include <stdbool.h>
#include <math.h>


typedef struct dequeue {
	int len;
	struct element *head;
	struct element *tail;
}dequeue;

typedef struct element {
	int data;
	struct element *left;
	struct element *right;
}element;


dequeue *make_dequeue(int input);
void push_back(dequeue *deq, int input);
void push_front(dequeue *deq, int input);
void print_dequeue(dequeue *deq);
int pop_front(dequeue *deq, bool clear);
dequeue *merge(dequeue *deq1, dequeue *deq2);
dequeue *sorted_dequeue(dequeue *deq);
int pop_back(dequeue *deq, bool clear);


#endif
