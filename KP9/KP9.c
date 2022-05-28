#include <stdio.h>
#include "stdlib.h"
#include "stdbool.h"
#include "string.h"

#define MAXLEN 1024


typedef struct element {
    float k;
    char v[MAXLEN];
}element;

typedef struct map{
    int max_size;
    int size;
    struct element **elements;
}map;

map *map_create(){
    map *m = malloc(sizeof(map));
    m->max_size = 10;
    m->size = 0;
    m->elements = (element**) malloc(sizeof(element*) * m->max_size);
    printf("...Table was created...\n");
	return m;
}


void map_add (map *m, float k, char *v) {
    if(m->size < m->max_size){
        element *u = malloc(sizeof(element));
        u->k = k;
        strcpy(u->v, v);
        m->elements[m->size] = u;
        m->size++;
    } else {
        printf("!!!Table is full!!!\n");
    }
}

void read_table(map *m, FILE *fin) {
    char str[MAXLEN];
    float key = 0;
    while(fscanf(fin, "%f", &key) != EOF) {
        fgets(str, MAXLEN, fin);
        int len = strlen(str);
        for(int i = 0; i != len; ++i) {
            if (str[i] == '\n')
                str[i] = '\000';
        }
        map_add(m, key, str);
    }
}

int contain (float n, float a[]) {
    for(int i = 0; i < 10; i++) {
        if(a[i] == n)
			return 1;
    }
    return 0;
}

void map_generate(map *m) {
    char marks[][MAXLEN] = {"Bentley    ",
                            "Mercedes   ",
                            "Skoda      ",
                            "Audi       ",
                            "Lada       ",
                            "BMW        ",
                            "Kia        ",
                            "Tesla      ",
                            "Daewoo     ",
                            "Toyota     ",
                            "Lamborghini",
                            "Chevrolet  ",
                            "Cadillac   "};
    float a[10];
    for(int i = 0; i < 10; i++) {
        a[10] = -1;
    }
    int j = 0;
    for(int i = 0; i < m->max_size - m->size + j; i++) {
        float r = rand()%13;
        while(contain(r, a)) {
            r = rand()%13;
        }
        a[j] = r;
        j++;
        map_add(m, (float)(rand()%10000)/1000, marks[(int)r]);
    }
}

void map_print(map *m) {
    for(int i = 0; i < m->size; i++)
		printf("! %f | %s |\n", m->elements[i]->k, m->elements[i]->v);
        printf("\n");
}

bool isInt(const char*str) {
    while(*str)  {
        if((*str< '0' || *str > '9') && *str != '.')
            return false;
        *str++;
    }
    return true;
}

element *search(map *m, float key, int left, int right) {
    int x = (right + left) / 2;
	if(left > right) {
    	return NULL;
	} else if(m->elements[x]->k < key) {
        return search(m, key, x+1, right);
    } else if(m->elements[x]->k > key) {
        return search(m, key, left, x-1);
    } else if(m->elements[x]->k == key) {
        return m->elements[x];
    }
    return NULL;
}

void siftDown(map *numbers, int root, float bottom) {
	int maxChild;
  	int done = 0;
  	while ((root * 2 <= bottom) && (!done)){
    	if (root * 2 == bottom)
      		maxChild = root * 2;
    	else if (numbers->elements[root * 2]->k > numbers->elements[root * 2 + 1]->k)
      		maxChild = root * 2;
    	else
      		maxChild = root * 2 + 1;
    	if (numbers->elements[root]->k < numbers->elements[maxChild]->k){
			element *temp = numbers->elements[root];
			numbers->elements[root] = numbers->elements[maxChild];
			numbers->elements[maxChild] = temp;
			root = maxChild;
		} else
			done = 1;
	}
}

void heapSort(map *numbers, int array_size) {
	for (int i = (array_size/2); i >= 0; i--)
		siftDown(numbers, i, array_size - 1);
	for (int i = array_size-1; i >= 1; i--) {
		element *temp = numbers->elements[0];
		numbers->elements[0] = numbers->elements[i];
    	numbers->elements[i] = temp;
		siftDown(numbers, 0, i-1);
	}
}


int main(int argc, const char * argv[]) {
    map *v = NULL;
    bool sorted = false;
    bool working = true;
    printf("Commands:\n1: Create table\n2: Add element\n3: Print table\n4: Fill table\n5: Sort table\n6: Search element\n\n\n");
    while(working) {
        int input = 0;
        char h[] = "";
        while(input == 0){
            scanf("%s", h);
            if(!strcmp("1",h)){
                input = 1;
            }
            else if(!strcmp("2",h)) {
                input = 2;
            }
            else if(!strcmp("3",h)) {
                input = 3;
            }
            else if(!strcmp("4",h)) {
                input = 4;
            }else if(!strcmp("5",h)) {
                input = 5;
            }else if(!strcmp("6",h)) {
                input = 6;
            }else {
                printf("!!!Wrong input!!!\n\n");
            }
        }
        printf("\n");
        switch(input){
            case 1:
            {
                if(v != NULL)
                    printf("!!!Table already exists!!!\n\n");
                else {
                    v = map_create();
                    FILE *fin = fopen("input.txt", "r");
                    read_table(v, fin);
                    fclose(fin);
                    sorted = false;
                }
                break;
            }
            case 2:
            {
                if(v != NULL){
                    char value[MAXLEN] = "";
                    float key = 0;
                    printf("...Enter  key of new unit...\n");
                    scanf("%f", &key);
                    sorted = false;
                    printf("...Enter  value of new unit...\n");
                    scanf("%s", value);
                    map_add(v, key, value);
                }
                else printf("!!!Table not exists!!!\n\n");
                break;
            }
            case 3:
            {
                if(v != NULL) {
                    map_print(v);
                    printf("\n");
                }
                else {
                    printf("!!!Table not exists\n\n");
                }
                break;
            }
            case 4: {
                map_generate(v);
                sorted = false;
                break;
            }
            case 5:
                if(v != NULL) {
                    heapSort(v, v->size);
                    sorted = true;
                    printf("...Table sorted...\n\n");
                }
                else {
                    printf("...Table not exists...\n\n");
                }
                break;
            case 6:
                if(v != NULL && sorted) {
                    float key = 0;
                    printf("...Enter key of element...\n\n");
                    scanf("%f", &key);
                    element *u = search(v, key, 0, v->size-1);
                    if(u == NULL) {
                        printf("!!!Key not exists!!!\n\n");
                    }
                    else 
						printf("Element value: %s\n\n", u->v);
                   
                }
                else {
                    printf("!!!Table not exists or not sorted!!!\n\n");
                }
                break;
                
        }
    }
    return 0;
}
