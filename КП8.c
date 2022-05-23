#include <stdio.h>
#include "stdlib.h"
#include "stdbool.h"
#include "string.h"


typedef struct list{
	int len;
	struct element *head;
}list;

typedef struct element{
	float data;
	struct element *prev;
	struct element *next;
}element;

list *create_list(){
	list *l = (list *) malloc(sizeof(list));
	l->head = (element *) malloc(sizeof(element));
	l->head->next = NULL;
	l->head->prev = NULL;
	l->head->data = 2048;
	l->len = 0;
	return l;
}

void add_element(list *l, float d){
	element *new_element = (element *) malloc(sizeof(element));
	new_element->data = d;
	new_element->next = NULL;
	element *iterator = l->head;
	while(iterator->next != NULL)
		iterator = iterator->next;
	new_element->prev = iterator;
	iterator->next = new_element;
	l->len++;
}

void print_list(list *l){
	element *iterator = l->head->next;
	while(iterator != NULL){
		printf("%f ", iterator->data);
		iterator = iterator->next;
	}
	printf("\n\n");
}

void print_len(list *l){
	printf("... Length of list = %d ...\n\n", l->len);
}

void delete_element(list *l, float d){
	element *iterator = l->head->next;
	while(true){
		if(iterator == NULL) {
			printf("!!!Element not exists!!!\n\n");
			break;
        } else if (iterator->data == d) {
			iterator->prev->next = iterator->next;
			if (iterator->next != NULL)
			    iterator->next->prev = iterator->prev;
			iterator->prev = NULL;
			iterator->next = NULL;
			free(iterator);
			l->len--;
			printf("...Element %f was deleted...\n\n", d);
			break;
		} else {
			iterator = iterator->next;
		}
	}
}

bool isReal(const char*str){
    while(*str)  {
        if((*str< '0' || *str > '9') && *str != '-')
            return false;
        *str++;
    }
    return true;
}

void copy_last_element(list *l, int k) {
	element *last = l->head;
	l->len += k;
	while(last->next != NULL)
		last = last->next;
	for (int i = 0; i < k; i++) {
		element *new_element = (element *) malloc(sizeof(element));
		element *iterator = (element *) malloc(sizeof(element));
		iterator = l->head->next;
		new_element->data = last->data;
		new_element->next = iterator;
		new_element->prev = NULL;
		iterator->prev = new_element;
		l->head->next = new_element;
	}
}

int main(int argc, const char *argv[]) {
	list *l = create_list();
	printf("Commands:\n1: Add element\n2: Delete element\n3: Print list\n4: List length\n5: Copy last element\n\n");
	while(true) {
        int input = 0;
        char h[] = "";
        while(input == 0){
            scanf("%s", h);
            if(!strcmp("1",h)){
                input = 1;
            } else if(!strcmp("2",h)) {
                input = 2;
            } else if(!strcmp("3",h)) {
                input = 3;
            } else if(!strcmp("4",h)) {
                input = 4;
            } else if(!strcmp("5",h)) {
                input = 5;
            } else {
                printf("!!!Incorrect command!!!\n\n");
            }
        }
        switch(input){
            case 1:
            {
                if(l->head != NULL){
                    float d = 0;
                    printf("...Enter value...\n");
                    scanf("%F", &d);
                    add_element(l, d);
                    printf("...Element %f was added...\n\n", d);
                }
                else printf("!!!Element not exists!!!\n\n");
                break;
            }
            case 2: 
			{
                if(l->head->next != NULL) {
                    float d;
                    printf("...Enter value...\n");
                    scanf("%f", &d);
                    delete_element(l, d);
                }
                else {
                    printf("!!!List is empty!!!\n");
                }
                break;
            }
            case 3:
            {
                if (l->head->next != NULL) {
                    print_list(l);
                }
                else {
                    printf("!!!List is empty!!!\n\n");
                }
                break;
            }
            case 4:
            {
                if(l != NULL) {
                    print_len(l);
                }
                else {
                    printf("!!!List not exists!!!\n\n");
                }
                break;
        	}
			case 5:
            {
                if(l->head->next != NULL) {
                	int k = 0;
                    printf("...Enter the number of copies...\n");
                    scanf("%d", &k);
                    copy_last_element(l, k);
                    printf("...List was updated...\n\n");
                } else {
                    printf("!!!List is empty!!!\n\n");
                }
                break;
        	}
        }
    }
    return 0;
}
