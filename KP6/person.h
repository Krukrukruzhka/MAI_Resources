#ifndef CLIONPROJECTS_PERSON_H
#define CLIONPROJECTS_PERSON_H

#define COUNT_OF_MARKS 7

typedef struct Person{
    char surname[50];
    char io[50];
    char sex[50];
    int group;
    int marks[COUNT_OF_MARKS];
} Person;

void Random(FILE* in);
int StudentReadTxt(Person *s, FILE *in);
void StudentWriteBin(Person *s, FILE *out);
void StudentPrint(Person *s);
int StudentReadBin(Person *s, FILE *in2);

#endif //CLIONPROJECTS_PERSON_H
