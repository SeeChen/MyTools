#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_BUFFER_SIZE 1024

char* RunCommand (

        char* command
) {

    char *str = (char*) malloc(MAX_BUFFER_SIZE * sizeof(char));
    snprintf(str, MAX_BUFFER_SIZE, "");

    FILE* pipe = popen(command, "r");

    if (pipe == NULL) {

        perror("p open");
        exit(EXIT_FAILURE);
    }

    char buffer[MAX_BUFFER_SIZE];
    while (fgets(buffer, MAX_BUFFER_SIZE, pipe) != NULL) {

        strcat(str, buffer);
    }

    if (pclose(pipe) == -1) {

        perror("p close");
        exit(EXIT_FAILURE);
    }

    return str;
}

int main() {

    int  words = 2;
    char command[][MAX_BUFFER_SIZE] = {
            "dir E:\\",
            "dir"
    };

    for (int i = 0; i < words; i++) {

        printf("%s", RunCommand(command[i]));
    }

    return 0;
}