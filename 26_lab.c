#include <stdio.h>
#include <math.h>
#include "stdlib.h"
#include "stdbool.h"
#include "string.h"


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


dequeue *make_dequeue(int input) {
	dequeue *deq = (dequeue *) malloc(sizeof(dequeue));
	element *first = (element *) malloc(sizeof(element));
	first->data = input;
	first->left = NULL;
	first->right = NULL;
	deq->len = 1;
	deq->head = first;
	deq->tail = first;
	return deq;
}

dequeue *make_empty_dequeue() {
    dequeue *deq = (dequeue *) malloc(sizeof(dequeue));
    deq->left = NULL;
    deq->right = NULL;
    deq->len = 0;
	return deq;
}

void push_back(dequeue *deq, int input) {
	element *new_element = (element *) malloc(sizeof(element));
	new_element->data = input;
	new_element->right = NULL;
	new_element->left = deq->tail;
	deq->tail->right = new_element;
	deq->tail = new_element;
		if (deq->len == 0)
		deq->head = new_element;
	deq->len++;
}

void push_front(dequeue *deq, int input) {
	element *new_element = (element *) malloc(sizeof(element));
	new_element->data = input;
	new_element->left = NULL;
	new_element->right = deq->head;
	deq->head->left = new_element;
	deq->head = new_element;
	if (deq->len == 0)
		deq->tail = new_element;
	deq->len++;
}

void print_dequeue(dequeue *deq) {
	element *iterator = deq->head;
	while (iterator != NULL) {
		printf("%d ", iterator->data);
		iterator = iterator->left;
	}
}

int pop_front(dequeue *deq, bool clear) {
	int output = deq->head->data;
	if (clear) {
		element *delete_element = deq->head;
		deq->head = deq->head->right;
		deq->head->left = NULL;
		if (deq->len == 1) {
			deq->tail = NULL;
		}
		free(delete_element);
		deq->len--;
	}
	return output;
}

dequeue *sort_deq(dequeue *deq) {
    int step = 2;
    int n = deq->len;
    dequeue **t = malloc(sizeof(dequeue)*n);
    for(int i = 0; i<n; i++) {
        dequeue *f = make_empty_dequeue();
        push_front(f, pop_front(d,) -> value); // EEEEEEEEEEEEEEEE
        t[i] = f;
    }
    int b = n;
    printf("Sorting =======\n");
    while(b > 1) {
        int i = 0;
        int k = 0;
        while(i < b) {
            dequeue *f = make_empty_dequeue();
            int count = (int)deck_size(t[i]) + (int)deck_size(t[i+1]); // EEEEEEEEEEEEEEEEEEEEEEEEE
            for(int j = 0; j<count; j++) {
                if(deck_is_empty(t[i])) { // EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE
                    unit *u = deck_pop_front(t[i+1]); // EEEEEEEEEEEEEEEEEEEEE
                    push_back(f, u->data);
                    free(u);
                }
                else if (deck_is_empty(t[i+1])) { // EEEEEEEEEEEEEEEEEEE
                    unit *u = deck_pop_front(t[i]); // EEEEEEEEEEEEEEEEEEEEE
                    push_back(f, u->data);
                    free(u);
                }
                else if(t[i]->left->value > t[i+1]->left->value) { // EEEEEEEEEEEEEEEEEEE
                    unit *u = deck_pop_front(t[i+1]); // EEEEEEEEEEEEEEEEEEEEEEEE
                    push_back(f, u->data);
                    free(u);
                }
                else {
                    unit *u = deck_pop_front(t[i]); // EEEEEEEEEEEEEEEEEEEEE
                    push_back(f, u->data);
                    free(u);
                }
            }
            print_dequeue(f);
            t[k] = f;
            k++;
            i+=step;
        }
        b = b / step + (b % step);
        printf("============\n");
    }
    return t[0];
}

int pop_back(dequeue *deq, bool clear) {
	int output = deq->tail->data;
	if (clear) {
		element *delete_element = deq->tail;
		deq->tail = deq->tail->left;
		deq->tail->right = NULL;
		if (deq->len == 1) {
			deq->head = NULL;
		}
		free(delete_element);
		deq->len--;
	}
	return output;
}


int main(void) {
	dequeue *deq;
	while (true) {
		int command;
		printf("Enter the command:\n1 Create dequeue\n2 Push in tail\n3 Get value from tail\n4 Push in head\n5 Get value from head\n6 Sort dequeue\n7 Print dequeue\n\n");
		scanf("%d", &command);
			switch(command):
				case 1:
				{
					printf("...Enter value...\n");
					int input;
					scanf("%d", &input);
					deq = make_dequeue(input);
					printf("...Dequeue was created...\n\n");
					break;
				}
				case 2:
				{
					printf("...Enter value...\n");
					int input;
					scanf("%d", &input);
					push_back(deq, input);
					printf("...Element was added...\n\n");
					break;
				}
				case 3:
				{
					printf("...Delete the last element? (1-yes, 0-no)...\n");
					int input;
					scanf("%d", &input);
					printf("%d \n\n", pop_back(deq, input));
					break;
				}
				case 4:
				{
					printf("...Enter value...\n");
					int input;
					scanf("%d", &input);
					push_front(deq, input);
					printf("...Element was added...\n\n");
					break;
				}
				case 5:
				{
					printf("...Delete the first element? (1-yes, 0-no)...\n");
					int input;
					scanf("%d", &input);
					printf("%d \n\n", pop_front(deq, input));
					break;	
				}
				case 6:
				{
					
					break;
				}
				case 7:
				{
					if (deq->head == NULL) {
						printf("!!!Dequeue is empty!!!\n\n");
					} else {
						print_dequeue(deq);
						printf("\n\n");	
					}
					break;
				}
				default:
				{
					printf("!!!Incorrect command!!!\n\n");
					break;
				}
		
	}
}
