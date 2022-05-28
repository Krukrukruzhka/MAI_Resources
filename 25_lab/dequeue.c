#include "dequeue.h"


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

void push_back(dequeue *deq, int input) {
	element *new_element = (element *) malloc(sizeof(element));
	new_element->data = input;
	new_element->right = NULL;
	new_element->left = deq->tail;
	if (deq->len != 0)
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
	if (deq->len != 0)
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
		iterator = iterator->right;
	}
}

int pop_front(dequeue *deq, bool clear) {
	int output = deq->head->data;
	if (clear) {
		element *delete_element = deq->head;
		deq->head = deq->head->right;
	    if (deq->head != NULL)
		    deq->head->left = NULL;
		if (deq->len == 1) {
			deq->tail = NULL;
		}
		free(delete_element);
		deq->len--;
	}
	return output;
}

dequeue *merge(dequeue *deq1, dequeue *deq2) {
    dequeue *deq = malloc(sizeof(dequeue));
    while (true)
        if(deq1->len != 0 && deq2->len != 0)
            if (pop_front(deq1, 0) <= pop_front(deq2, 0))
                push_back(deq, pop_front(deq1, 1));
            else
                push_back(deq, pop_front(deq2, 1));
        else if (deq1->len != 0)
            push_back(deq, pop_front(deq1, 1));
        else if (deq2->len != 0)
            push_back(deq, pop_front(deq2, 1));
        else {
            // free(deq1);
            // free(deq2);
            return deq;
        }
}

dequeue *sorted_dequeue(dequeue *deq) {
    dequeue *merged_deq;
    if (deq->len == 1) {
        merged_deq = make_dequeue(pop_front(deq, 1));
        free(deq);
        return merged_deq;    
    }
    else {
        dequeue *deq1 = make_dequeue(pop_front(deq, 1));
        dequeue *deq2 = make_dequeue(pop_front(deq, 1));
        int k = deq->len;
        for(int i = 0; i < k/2; i++) {
            push_back(deq1, pop_front(deq, 1));
            push_back(deq2, pop_front(deq, 1));
        }
        if (deq->len != 0)
            push_back(deq2, pop_front(deq, 1));
        free(deq);
        deq1 = sorted_dequeue(deq1);
        deq2 = sorted_dequeue(deq2);
        merged_deq = merge(deq1, deq2);
        return merged_deq;    
    }
}

int pop_back(dequeue *deq, bool clear) {
	int output = deq->tail->data;
	if (clear) {
		element *delete_element = deq->tail;
		deq->tail = deq->tail->left;
		if (deq->tail != NULL)
		    deq->tail->right = NULL;
		if (deq->len == 1) {
			deq->head = NULL;
		}
		free(delete_element);
		deq->len--;
	}
	return output;
}
