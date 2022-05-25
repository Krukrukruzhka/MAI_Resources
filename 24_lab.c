#include <stdio.h>
#include <math.h>
#include "stdlib.h"
#include "stdbool.h"
#include "string.h"


typedef struct unit {
    char data[50];
    struct unit *left;
    struct unit *right;
}unit;


int score(unit *n) {
    if (n->data[0] == '+')
        return score(n->left) + score(n->right);
    else if (n->data[0] == '-')
        return score(n->left) - score(n->right);
    else if (n->data[0] == '*')
        return score(n->left) * score(n->right);
    else if (n->data[0] == '/')
        if (score(n->left) == score(n->right))
            return 1;
        else
            return 10000;
    else if (n->data[0] == '^')
        return (int) pow(score(n->left), score(n->right));
    else
        return (int)strtol(n->data, NULL, 10);
}

bool is_op(char a) {
    if(a == '*' || a == '^' || a == '/' || a == '+' || a == '-') 
		return true;
    else 
		return false;
}

int define_priority (char a) {
	if (a == '-' || a == '+')
    	return 1;
    else if (a == '*')
    	return 2;
    else if (a == '/')
    	return 3;
    else if (a == '^')
    	return 4;
    else
    	return 5;
}

unit *make_tree(char expr[], int first, int last) {
    int prior, min_prior = 5, k, depth = 0;
    unit *tree = malloc(sizeof(unit));
    for (int i = first; i <= last; ++i) {
        if (expr[i] == '(') {
            depth++;
            continue;
    	}
        if (expr[i] == ')') {
            depth--;
            continue;
        }
        if (depth>0){
            continue;
        }
        prior = define_priority(expr[i]);
    	if (prior <= min_prior) {
            min_prior = prior;
            k = i;
        }
    }
    if (depth !=0) {
        printf("!!!Wrong expression!!!\n\n");
        exit (1);
    }
    int l;
    if (min_prior == 5) {
        if (expr[first] == '(' && expr[last] == ')') {
            free(tree);
            return make_tree(expr, first +1, last - 1);
        } else {
        	l = last - first + 1;
            for (int i = 0; i < l; i++ ) {
                tree->data[i] = expr[first+i];
            }
            tree->data[l] = '\n';
            tree->left = NULL;
            tree->right = NULL;
            return tree;
        }
    }
    tree->data[0] = expr[k];
    tree->data[1] = '\n';
    tree->left = make_tree(expr, first, k-1);
    tree->right = make_tree(expr, k+1, last);
    return tree;
}

unit *clear_ones(unit *n) {
    if (define_priority(n->data[0]) == 2) {
    	if (n->left != NULL) 
    	    if (score(n->left) == 1)
    		    return clear_ones(n->right);
		if (n->right != NULL)
			if (score(n->right) == 1)
			    return clear_ones(n->left);
	} else {
		if (n->left != NULL)
			n->left = clear_ones(n->left);
		if (n->right != NULL)	
			n->right = clear_ones(n->right);
	}
	return n;
}


void printTree (unit *n, int hight) {
    for (int i = 0; i < hight - 1; ++i) {
        printf("-");
    }
    if (hight != 0)
        printf("-");
        
    if (hight != 0) {
        printf(" %s", n->data);
    }
    else {
        printf(" %s", n->data);
    }
    
    int hight2 = hight;
    if (n->left) {
        printTree(n->left, ++hight2);
    }
    hight2 = hight;
    if (n->right) {
        printTree(n->right, ++hight2);
    }
}

void print_tree(unit *u, int l) {
    if (u->right != NULL) print_tree(u->right, l+1);
    for(int i = 0; i < l; ++i) {
        printf("   ");
    }
    printf("%5s", u->data);
    if (u->left != NULL)
		print_tree(u->left, l+1);
}

void print_expression(unit *u) {
    if (u==NULL) {
        return;
    }
    if (define_priority(u->data[0])!=5 && define_priority(u->left->data[0])!=5 && define_priority(u->data[0]) > define_priority(u->left->data[0])  || u->data[0] == '^' && u->left->data[0] == '^') {
        printf("(");
        print_expression(u->left);
        printf(")");
    } else 
		print_expression(u->left);
    for (int i = 0; i < 50; ++i) {
        if (u->data[i] == '\n') {
            break;
        }
        printf("%c", u->data[i]);
    }
    if (define_priority(u->data[0])!=5 && define_priority(u->right->data[0])!=5 && define_priority(u->data[0]) > define_priority(u->right->data[0])  || u->data[0] == '^' && u->right->data[0] == '^') {
        printf("(");
        print_expression(u->right);
        printf(")");
    } else 
		print_expression(u->right);
}


int main(void) {
    unit *t = NULL;
	printf("Enter the command:\n1 Create tree\n2 Transforn expression\n3 Print tree\n4 Print expression\n\n");
    while (true) {
        int opt;
        scanf("%d", &opt);
        switch (opt) {
            case 1: {
                printf("...Enter an expression...\n");
                char expression[1000];
                scanf("%s", expression);
                int n = 0;
                while (expression[n] != '\0') {
                    n++;
                }
                t = make_tree(expression, 0, n-1);
                printf("...Tree was created...\n\n");
                break;
            }
            case 2: {
                t = clear_ones(t);
                printf("...Ones was cleared...\n\n");
                break;
            }
            case 3: {
                printf("\n");
                printTree(t, 0);
                printf("\n\n");
                break;
            }
            case 4: {
                print_expression(t);
                printf("\n");
                break;
            }
            default:{
                printf("!!!Incorrect command!!!\n\n");
				break;
			}
    	}
    }
    return 0;
}
