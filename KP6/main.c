#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include "person.h"

#define COUNT_OF_MARKS 7

void Usage() {
    printf("Wrong input!\n");
    printf("Usage: -f <input file> (for printing database)\n");
    printf("       -p <input file> (for special task)\n");
    exit(404);
}

int main(int argc, char* argv[])
{
    srand(time(NULL));
    if (argc < 3 || argc > 4) {
        Usage();
    }
    Person student;
    FILE *fIn2 = fopen(argv[2], "w");
    FILE *fOut = fopen("output.txt", "w");
    if (!fIn2 || !fOut) {
        printf("Can't open file!\n");
    }
    Random(fIn2);
    fclose(fIn2);
    FILE *fIn = fopen(argv[2], "r");
    fseek(fIn, 0, SEEK_SET);
    if (strcmp(argv[1],"-f") == 0) {
        printf("            Surname   |  IO  |     Gender     |    Group    |  Marks\n");
        while (StudentReadTxt(&student, fIn)) {
            StudentPrint(&student);
        }
        fclose(fIn);
        fclose(fOut);
        return 0;
    }
    else if (strcmp(argv[1],"-p") == 0) {
        while (StudentReadTxt(&student, fIn)) {
            StudentWriteBin(&student, fOut);
        }
        StudentWriteBin(&student, fOut);
        fclose(fOut);
        fclose(fIn);
        FILE *in2 = fopen("output.txt", "r");
        fseek(in2, 0, SEEK_SET);
        int target = 0;
        while (StudentReadBin(&student, in2)) {
            int count = 0;
            for (int i = 0; i < COUNT_OF_MARKS; i++)
                if (student.marks[i] == 3)
                    count++;
            if (count > 2 && atoi(argv[3]) == student.group && strcmp(student.sex, "male")) {
                StudentPrint(&student);
                target++;
            }
        }
        printf("\n\nAnswer: %d", target);
        fclose(in2);
        return 0;
    }
    else
        Usage();
    return 0;
}