!#/bin/bash
awk 'BEGIN{print"      School average rating \n"};
    {
        total = 0
        for(i = 2; i <= NF; i++) {
            total += $i
        }
        printf "%s %f\n", $1, total/(NF-1);
    }' lab_20.txt