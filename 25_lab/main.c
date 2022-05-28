#include <stdio.h>
#include <math.h>
#include "stdlib.h"
#include "stdbool.h"
#include "string.h"
#include "dequeue.h"


int main(void) {
	dequeue *deq;
	printf("Enter the command:\n1 Create dequeue\n2 Push in tail\n3 Get value from tail\n4 Push in head\n5 Get value from head\n6 Sort dequeue\n7 Print dequeue\n\n");
	while (true) {
		int command;
		scanf("%d", &command);
		switch(command) {
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
			    if (deq->head == NULL) {
			        printf("!!!Dequeue is empty!!!\n\n");
			    } else {
    			    printf("...Delete the last element? (1-yes, 0-no)...\n");
    				int input;
    				scanf("%d", &input);
    				printf("%d \n\n", pop_back(deq, input));
			    }
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
			    if (deq->head == NULL)
			        printf("!!!Dequeue is empty!!!\n\n");
				else {
    				printf("...Delete the first element? (1-yes, 0-no)...\n");
    				int input;
    				scanf("%d", &input);
    				printf("%d \n\n", pop_front(deq, input));
				}
				break;	
			}
			case 6:
			{
				if (deq->len == 0)
				    printf("!!!Dequeue is empty!!!\n\n");
				else
				    deq = sorted_dequeue(deq);
				    printf("...Dequeue was sorted...\n\n");
				break;
			}
			case 7:
			{
				if (deq->head == NULL) {
					printf("!!!Dequeue is empty!!!\n\n");
				} else {
					print_dequeue(deq);
					printf("\nLength = %d", deq->len);
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
	return 0;
}

