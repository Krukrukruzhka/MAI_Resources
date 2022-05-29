#include <stdio.h>
#include <stdlib.h>
#include "person.h"

#define COUNT_OF_MARKS 7

void Random(FILE *in){
    char male_surnames[][50] = {"Ivanov", "Petrov", "Sidorov", "Loopin", "Popov", "Zhukov", "Morozov",
                      "Okunev", "Podolopin", "Ulukaev", "Ivanenko", "Konovalov", "Razumov", "Klopov",
                      "Polodko", "Potelin"};
    char female_surnames[][50] = {"Ivanova", "Petrova", "Sidorova", "Loopina", "Popova", "Zhukova", "Morozova",
                                  "Okuneva", "Podolopina", "Ulukaeva", "Ivanenko", "Konovalova", "Razumova", "Klopova",
                                  "Polodko", "Potelina"};
    char iio[26] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    char sex[][7] = {"male", "female"};
    for (int i = 0; i < 15; i++) {
        int pol = rand()%2;
        if (pol)
            fprintf(in, "%s ", male_surnames[rand()%16]);
        else
            fprintf(in, "%s ", female_surnames[rand()%16]); // surname
        fprintf(in, "%c.%c. ", iio[rand()%26], iio[rand()%26]); //initials
        fprintf(in, "%s ", sex[pol]); // sex
        fprintf(in, "%d", rand()%4); // group
        for (int i = 0; i < COUNT_OF_MARKS; i++)
            fprintf(in, " %d", rand()%4+2);
        fprintf(in, " \n");
    }
}

int StudentReadTxt(Person *s, FILE *in) {
    fscanf(in, "%s", s->surname);
    fscanf(in, "%s", s->io);
    fscanf(in, "%s", s->sex);
    fscanf(in, "%d", &(s->group));
    for (int i = 0; i < COUNT_OF_MARKS; i++)
        fscanf(in, "%d", &(s->marks[i]));
    return !feof(in);
}

void StudentWriteBin(Person *s, FILE *out) {
    fwrite(s->surname, sizeof(char), 50, out);
    fwrite(s->io, sizeof(char), 50, out);
    fwrite(s->sex, sizeof(char), 50, out);
    fwrite(&(s->group), sizeof(int), 1, out);
    for (int i = 0; i < COUNT_OF_MARKS; i++)
        fwrite(&(s->marks[i]), sizeof(int), 1, out);
}

void StudentPrint(Person *s){
    printf("         -------------|------|----------------|-------------|");
    for (int i = 0; i < COUNT_OF_MARKS; i++)
        printf("-------|");
    printf("\n");
    printf("%20s  |", s->surname);
    printf("  %s  |", s->io);
    printf("   %8s     |", s->sex);
    printf("%8d\t    |", (s->group));
    for (int i = 0; i < COUNT_OF_MARKS; i++)
        printf("%5d\t |", (s->marks[i]));
    printf("\n");
}

int StudentReadBin(Person *s, FILE *in2) {
    fread(s->surname, sizeof(char), 50, in2);
    fread(s->io, sizeof(char), 50, in2);
    fread(s->sex, sizeof(char), 50, in2);
    fread(&(s->group), sizeof(int), 1, in2);
    for (int i = 0; i < COUNT_OF_MARKS; i++)
        fread(&(s->marks[i]), sizeof(int), 1, in2);
    return !feof(in2);
}
