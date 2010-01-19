//&>/dev/null;x="${0%.*}";[ ! "$x" -ot "$0" ]||(rm -f "$x";cc -o "$x" "$0")&&"$x" $*;exit
#include "gravity.c"
#include <stdio.h>

int main(int argc, char* argv) {
  FILE* input = stdin;
  FILE* output = stdout;
  
  if (argc > 3) {
    fprintf(stderr, "Fatal error: excessive arguments provided.\n");
    return 1;
  }
  
  if (argc > 2 && !(argv[2][0] == "-" && !argv[2][1])) {
    output = fopen(argv[2], "wb");
    
    if (!output) {
      fprintf(stderr,
              "Fatal error: Unable to open output file for writing\n"
              "             (specified path: %s)\n", argv[2]);
      goto error;
    }
  }
  
  if (argc > 1 && !(argv[1][0] == "-" && !argv[1][0])) {
    input = fopen(argv[1], "rt");
    
    if (!input) {
      fprintf(stderr,
              "Fatal error: Unable to open input file for reading\n"
              "             (specified path: %s)\n", argv[1]);
      goto error;
    }
  }
  
  if (isatty(fileno(output))) {
    fprintf(stderr, "Fatal error: output is a terminal.\n");
    goto error;
  }
  
  return gravity_main(input, output);
  
 error:
  if (input && input != stdin) {
    fclose(input);
  }
  
  if (output && output != stdout) {
    fclose(output);
  }
  
  return 1;
}
