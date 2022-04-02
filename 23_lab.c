#include <stdio.h>
#include "stdlib.h"
#include "stdbool.h"
#include "string.h"

typedef struct BinaryTree {
    struct BinaryTree *left;
    struct BinaryTree *right;
    int key;
} BinaryTree;

BinaryTree *makeBinaryTree(int key) {
    BinaryTree *n = (BinaryTree*)malloc(sizeof(BinaryTree));
    n->key = key;
    n->left = NULL;
    n->right = NULL;
    return n;
}

void freeBinaryTree(BinaryTree *n) {
    printf("the tree has been cleaned %d\n", n->key);
    if (n->left)
        freeBinaryTree(n->left);
    if (n->right)
        freeBinaryTree(n->right);
    free(n);
}

void printTree (BinaryTree *n, int hight) {
    for (int i = 0; i < hight - 1; ++i) {
        printf("- ");
    }
    if (hight != 0)
        printf("- ");
        
    if (hight != 0) {
        printf("%d", n->key);
    }
    else {
        printf("%d", n->key);
    }
    
    printf("\n");
    int hight2 = hight;
    if (n->left) {
        printTree(n->left, ++hight2);
    }
    hight2 = hight;
    if (n->right) {
        printTree(n->right, ++hight2);
    }
}

BinaryTree *findBinaryTree(BinaryTree *n, int key) {
    if (n == NULL || n->key == key) {
        return n;
    }
    if (key < n->key) {
        return findBinaryTree(n->left, key);
    }
    else {
        return findBinaryTree(n->right, key);
    }
}

void addBinaryTree(BinaryTree *n, int key) {
    if (findBinaryTree(n, key)) {
        printf("!!!error, element already created!!!\n");
    }
    else {
        if (n->key > key) {
            if(n->left == NULL)
                n->left = makeBinaryTree(key);
            else
                addBinaryTree(n->left, key);
        }
        else {
            if(n->right == NULL)
                n->right = makeBinaryTree(key);
            else
                addBinaryTree(n->right, key);
        }
    }
}

BinaryTree *MinBinaryTree(BinaryTree *n) {
    if (n->left == NULL) {
        return n;
    }
    return MinBinaryTree(n->left);
}

BinaryTree *MaxBinaryTree(BinaryTree *n) {
    if (n->right == NULL) {
        return n;
    }
    return MaxBinaryTree(n->right);
}

BinaryTree *removeBinaryTree(BinaryTree *n, int key) {
    if (n->key > key) {
        n->left = removeBinaryTree(n->left, key);
    }
    else if (n->key < key) {
        n->right = removeBinaryTree(n->right, key);
    }
    else if (n->right != NULL && n->left != NULL) {
        n->key = MinBinaryTree(n->right)->key;
        n->right = removeBinaryTree(n->right, n->key);
    }
    else {
        if (n->right != NULL) {
            BinaryTree *t = n->right;
            free(n);
            n = t;
        } else if (n->left != NULL) {
            BinaryTree *t = n->left;
            free(n);
            n = t;
        } else {
            free(n);
            n = NULL;
        }
    }
    return n;
}

void leafBin(BinaryTree *n, int *count) {
    if (n->left) {
        leafBin(n->left, count);
    }
    if (n->right) {
        leafBin(n->right, count);
    }
    if (n->left == NULL && n->right == NULL) {
        ++*count;
    }
}
int leafsCount(BinaryTree *n) {
    int count = 0;
    leafBin(n, &count);
    return count;
}

bool isInt(const char*str) {
    while(*str)  {
        if((*str< '0' || *str > '9') && *str != '-' && *str != '.')
            return false;
        *str++;
    }
    return true;
}

void error() {
    printf("!! you are stupid, give me right value !!\n\n");
}

int main() {
    
    BinaryTree *nb;
    bool wasStarded = true;
    printf("...started...\n\n");

    int root;
    char c[] = "";
    bool accepted = true;
    int x = 0;
    while (accepted) {
        printf("it's a creation of new tree\n please enter root\n");
        scanf("%s", c);
        if (isInt(c)){
            root = atoi(c);
            accepted = false;
        } else{
            error();
        }
    }
    nb = makeBinaryTree(root);
    printf("...the tree has been created...\n");
    printf("\ninstruction:\n 1: put new leaf  2: delete element  3: print tree  4: print count of leafs  5: exit\n\n");
    
    while (wasStarded) {
        int status = 0;
        char check[] = "";
        while (status == 0) {
            scanf("%s", check);
            if(!strcmp("1",check)){
                status = 1;
            }
            else if(!strcmp("2",check)) {
                status = 2;
            }
            else if(!strcmp("3",check)) {
                status = 3;
            }
            else if(!strcmp("4",check)) {
                status = 4;
            }else if(!strcmp("5",check)) {
                status = 5;
            }else {
                error();
            }
        }
        
        switch (status) {
            case 1:
                printf(" ");
                int t = 0;
                char c[] = "";
                accepted = true;
                while (accepted) {
                    printf("give me the key of new leaf\n");
                    scanf("%s", c);
                    if (isInt(c)){
                        t = atoi(c);
                        accepted = false;
                    } else{
                        error();
                    }
                }
                addBinaryTree(nb, t);
                printf("...the leaf has been added...\n\n");
                break;
            
            case 2:
                printf(" ");
                int x = 0;
                char h[] = "";
                accepted = true;
                while (accepted) {
                    printf("enter the key\n");
                    scanf("%s", h);
                    if (isInt(h)){
                        x = atoi(h);
                        accepted = false;
                    } else{
                        error();
                    }
                }
                if (findBinaryTree(nb, x) == NULL) {
                    error();
                }
                else {
                    if (nb->key == x && nb->right == NULL && nb->left == NULL) {
                        freeBinaryTree(nb);
                        nb = NULL;
                    }
                    else {
                        nb = removeBinaryTree(nb, x);
                    }
                    printf("...the subtree has been deleted...\n\n");
                }
                break;
            
            case 3:
                printTree(nb, 0);
                printf("\n");
                break;
            
            case 4:
                printf("%d leafs\n\n", leafsCount(nb));
                break;
            
            case 5:
                printf("...end of program...\n");
                wasStarded = false;
                break;
            
            default:
                error();
                break;
        }
    }
    freeBinaryTree(nb);
    return 0;
}
